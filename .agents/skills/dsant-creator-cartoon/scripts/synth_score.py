#!/usr/bin/env python3
"""Original deterministic draft score and event sounds. No model, network or paid API."""
import argparse,json,wave
from pathlib import Path
import numpy as np
from validate_episode import validate
SR=48000

def synth(p,out):
    errors=validate(p)
    if errors:raise ValueError('; '.join(errors))
    duration=p['video']['durationInFrames']/p['video']['fps'];fps=p['video']['fps']
    n=round(duration*SR);music=np.zeros(n);fx=np.zeros(n);rng=np.random.default_rng(p['seed'])
    bpm=float(p['audio'].get('bpm',104))
    if not 30<=bpm<=240:raise ValueError('BPM fora do intervalo 30–240')
    def add(dst,x,at):
        i=round(at*SR);end=min(i+len(x),n)
        if i>=0 and end>i:dst[i:end]+=x[:end-i]
    def note(hz,seconds):
        t=np.arange(round(seconds*SR))/SR
        return (np.sin(2*np.pi*hz*t)+.2*np.sin(4*np.pi*hz*t))*(1-np.exp(-t*200))*np.exp(-t*7)
    # Original procedural composition; bpm/style are choices, never inferred measurements.
    electronic=p['audio'].get('style')=='electronic_dnb_original'
    beat=60/bpm
    for j,at in enumerate(np.arange(0,duration,beat)):
        hz=[220,261.626,329.628,293.665,246.942,329.628,261.626,196][j%8]
        add(music,.025*note(hz,.6) if electronic else .06*note(hz,.6),at)
    if electronic:
        # Energy follows the episode, leaving room for reactions instead of a continuous drop.
        for j,at in enumerate(np.arange(0,duration,beat/2)):
            fraction=at/duration
            gain=.45 if fraction<.3 else .7 if fraction<.55 else .18 if fraction<.65 else 1 if fraction<.9 else .4
            t=np.arange(round(.15*SR))/SR
            hat=rng.normal(size=len(t))*np.exp(-t*80)
            hat=hat-np.convolve(hat,np.ones(13)/13,mode='same')
            add(music,.014*gain*hat,at)
            if j%8 in [0,5]:
                t=np.arange(round(.22*SR))/SR
                kick=np.sin(2*np.pi*(48*t+55*(1-np.exp(-t*25))/25))*np.exp(-t*20)
                add(music,.13*gain*kick,at)
            if j%8 in [2,6]:
                t=np.arange(round(.18*SR))/SR
                snare=(rng.normal(size=len(t))*.6+np.sin(2*np.pi*180*t)*.4)*np.exp(-t*27)
                add(music,.055*gain*snare,at)
            if j%2==0:
                t=np.arange(round(beat*.85*SR))/SR;hz=[55,65.406,49,58.27][(j//8)%4]
                bass=(np.sin(2*np.pi*hz*t)+.18*np.sin(2*np.pi*hz*3*t))*(.7+.3*np.sin(2*np.pi*5*t))
                bass*=np.minimum(t/.012,1)*np.minimum((t[-1]-t)/.025,1)
                add(music,.07*gain*bass,at)
    for s in p['scenes']:
        for c in s.get('audio_cues',[]):
            at=c['frame']/fps;d=(c['endFrame']-c['frame'])/fps;t=np.arange(round(d*SR))/SR
            kind=c.get('kind','click')
            if kind=='silence':
                a=round(at*SR);b=min(n,round((at+d)*SR));music[a:b]=0;continue
            if kind=='impact':x=.22*np.sin(2*np.pi*65*t)*np.exp(-t*22)+.05*rng.normal(size=len(t))*np.exp(-t*70)
            elif kind=='whoosh':x=.04*rng.normal(size=len(t))*np.sin(np.pi*t/d)**2
            elif kind=='idea':x=.1*note(660,d)
            else:x=.08*note(1350,d)
            add(fx,x,at)
    # Smooth score edges and authored silences to avoid discontinuity clicks.
    music=np.convolve(music,np.ones(49)/49,mode='same')
    fade=np.minimum(np.arange(n)/(SR*.02),1)*np.minimum((n-1-np.arange(n))/(SR*.06),1)
    out.mkdir(parents=True,exist_ok=False)
    for name,x in [('music',music),('sfx',fx),('mix-preview',music+fx)]:
        x=x*fade;peak=float(np.max(np.abs(x)))
        if peak>.8:x*=.8/peak
        data=(np.clip(x,-1,1)*32767).astype('<i2')
        with wave.open(str(out/f'{name}.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(data.tobytes())
    (out/'report.json').write_text(json.dumps({'seconds':duration,'sample_rate':SR,'seed':p['seed'],'bpm':bpm,'cost':0,'voice_included':False,'mastered':False,'audition_required':True},indent=2))
    print(f'{duration:.3f}s: 3 stems/previews gerados; masterização e audição pendentes.')
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('episode',type=Path);a.add_argument('out',type=Path);p=a.parse_args();synth(json.loads(p.episode.read_text()),p.out)
