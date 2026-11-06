import numpy as np,wave,json
from pathlib import Path

p=Path(__file__).parent;sr=48000;D=sum(x['frames'] for x in json.loads((p/'src/data.json').read_text()))/30;n=round(D*sr);t=np.arange(n)/sr;rng=np.random.default_rng(14)
noise=rng.normal(size=n)
wind=np.convolve(noise,np.ones(70)/70,mode='same')*.009
street=wind.copy()
engine=(np.sin(2*np.pi*58*t)+.4*np.sin(2*np.pi*116*t)+.2*np.sin(2*np.pi*174*t))*(.7+.3*np.sin(2*np.pi*14*t))
env=np.where(t<6.9,.045,np.where(t<8.1,.045*np.exp(-(t-6.9)*5),0));street+=engine*env
for at in [7.02,7.3,7.55,7.85]:
 a=int(at*sr);u=np.arange(int(.22*sr))/sr;x=(np.sin(2*np.pi*45*u)+rng.normal(size=len(u))*.4)*np.exp(-u*26)*.15;street[a:a+len(x)]+=x
for at in np.arange(8.5,14.6,.55):
 a=int(at*sr);u=np.arange(int(.13*sr))/sr;x=(np.sin(2*np.pi*110*u)*.5+rng.normal(size=len(u))*.4)*np.exp(-u*38)*.06;street[a:a+len(x)]+=x
for at in [16,19.4,24]:
 a=int(at*sr);u=np.arange(int(.18*sr))/sr;x=np.sin(2*np.pi*(1600*u+900*u*u))*np.sin(np.pi*u/.18)**2*.009;street[a:a+len(x)]+=x
for at in [15.4,15.65]:
 a=int(at*sr);u=np.arange(int(.09*sr))/sr;x=np.sin(2*np.pi*800*u)*np.exp(-u*60)*.045;street[a:a+len(x)]+=x
street*=np.minimum(t/.03,1)*np.minimum((D-t)/.25,1)
with wave.open(str(p/'public/ambience.wav'),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.stack([street,street*.95],axis=1)*32767).astype('<i2').tobytes())
