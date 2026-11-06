"""Mix deterministic original score, synthesized effects and measured neural narration."""
import json
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import butter,sosfilt
P=Path(__file__).resolve().parents[1]
SR=48000;D=40;N=SR*D
rng=np.random.default_rng(4201)
voice=np.zeros(N);fx=np.zeros(N);music=np.zeros(N)
vo=json.loads((P/'src/data/vo.json').read_text());tim=json.loads((P/'src/data/timing.json').read_text())
starts=tim['starts'];bounds=np.array(tim['bounds'])/30

def add(dst,x,t,g=1):
 a=int(t*SR);b=min(a+len(x),N)
 if b>a:dst[a:b]+=x[:b-a]*g

def pluck(hz,dur=.8):
 t=np.arange(int(dur*SR))/SR
 env=(1-np.exp(-t*180))*np.exp(-t*5)
 return (np.sin(2*np.pi*hz*t)+.24*np.sin(2*np.pi*hz*2*t)+.08*np.sin(2*np.pi*hz*3*t))*env

def impact(dur=.35):
 t=np.arange(int(dur*SR))/SR
 return .7*np.sin(2*np.pi*(48*t+14*(1-np.exp(-t*12))/12))*np.exp(-t*18)+.15*rng.normal(0,1,len(t))*np.exp(-t*80)

def click(dur=.08):
 t=np.arange(int(dur*SR))/SR
 return (.7*np.sin(2*np.pi*1750*t)+.35*rng.normal(0,1,len(t)))*np.exp(-t*90)

def whoosh(dur=.6):
 t=np.arange(int(dur*SR))/SR
 noise=sosfilt(butter(2,[350,4200],fs=SR,btype='bandpass',output='sos'),rng.normal(0,1,len(t)))
 return noise*np.sin(np.pi*t/dur)**3

def cue(scene,index):return starts[f's{scene}']+vo[f's{scene}']['words'][index]['start']
for k,v in vo.items():
 x,sr=sf.read(P/f'public/audio/vo/{k}.wav');assert sr==SR
 add(voice,x,starts[k])
# Subtle pulse in D minor: original notes, no sampled or third-party music.
beat=60/106
for k,t in enumerate(np.arange(0,37,beat)):
 root=[73.416,65.406,87.307,65.406][(k//8)%4]
 add(music,pluck(root,1.2),t,.018 if k%4==0 else .008)
 if k%2==1:add(music,pluck(root*4,.8),t,.006)
 if k%4 in [1,3]:add(music,click(.04),t,.009)
for t in bounds[1:-1]:add(fx,whoosh(.42),max(t-.2,0),.028)
add(fx,click(),.02,.12);add(fx,impact(),.4,.17)
add(fx,impact(),bounds[1]+.1,.1)
add(fx,whoosh(.75),cue(2,6)-.2,.075)
for t in [bounds[2]+.1,cue(3,5),cue(3,10)]:add(fx,click(),t,.075)
for n,hz in zip([3,4,6],[587.33,698.46,880]):add(fx,pluck(hz,.35),cue(4,n),.036)
add(fx,impact(),bounds[3]+.5,.06)
add(fx,pluck(440,.7),cue(5,2),.025)
add(fx,click(.12),cue(7,2),.09)
# Final soft consonant chord, leaving the contact legible and unhurried.
for hz in [146.832,220,293.665]:add(music,pluck(hz,2.4),36.4,.012)
# Duck the score around actual speech windows.
duck=np.ones(N)
for k,v in vo.items():
 a=max(0,int((starts[k]-.08)*SR));b=min(N,int((starts[k]+v['seconds']+.12)*SR));duck[a:b]=.42
music*=duck
fade=np.minimum(np.arange(N)/(SR*.25),1)*np.minimum((N-1-np.arange(N))/(SR*.8),1)
mix=(voice+fx+music)*fade
assert np.isfinite(mix).all()
peak=float(np.max(abs(mix)))
if peak>.94:mix*=.94/peak
stereo=np.stack([mix,mix],axis=1)
# Slight ambience width, keeping the voice centered.
stereo[:,0]+=music*.06;stereo[:,1]-=music*.06
sf.write(P/'public/audio/mix.wav',stereo,SR,subtype='PCM_24')
(P/'out/mix-report.json').write_text(json.dumps({'seconds':D,'peak_before_master_dbfs':20*np.log10(np.max(abs(stereo))),'speech_end':tim['speechEnd'],'voice':'pt-BR-AntonioNeural','source_rate':'+2%','post_tempo':1.06,'score':'original deterministic synthesized','effects':'original synthesized'},indent=2))
# Captions file for reuse without baked-in typography.
words=[]
for k,v in vo.items():
 for w in v['words']:words.append({'text':w['text'],'start':starts[k]+w['start'],'end':starts[k]+w['end']})
def ts(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(P/'out/rr-painel-legendas.srt').write_text('\n\n'.join(f"{i+1}\n{ts(w['start'])} --> {ts(w['end'])}\n{w['text']}" for i,w in enumerate(words)),encoding='utf-8')
print(json.loads((P/'out/mix-report.json').read_text()))
