#!/usr/bin/env python3
"""Inspect locally, without uploading video; requires ffmpeg/ffprobe and Pillow."""
import argparse,json,subprocess,re,hashlib
from pathlib import Path
from PIL import Image,ImageDraw

def run(args):
    return subprocess.run(args,check=True,capture_output=True,text=True)

def analyze(src,out,step):
    src=src.resolve()
    if not src.is_file(): raise ValueError('Vídeo não encontrado')
    if step<=0: raise ValueError('step deve ser positivo')
    out.mkdir(parents=True,exist_ok=False)
    meta=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(src)]).stdout)
    frames=out/'frames';frames.mkdir()
    run(['ffmpeg','-v','error','-i',str(src),'-vf',f'fps=1/{step},scale=240:-2','-vsync','vfr',str(frames/'%06d.jpg')])
    paths=sorted(frames.glob('*.jpg'))
    for first in range(0,len(paths),24):
        batch=paths[first:first+24]; w,h=Image.open(batch[0]).size
        sheet=Image.new('RGB',(w*6,(h+24)*4),'#202329'); d=ImageDraw.Draw(sheet)
        for j,p in enumerate(batch):
            x=(j%6)*w;y=(j//6)*(h+24)
            with Image.open(p) as im: sheet.paste(im,(x,y))
            d.text((x+5,y+h+4),f'~{(first+j)*step:.2f}s',(255,255,255))
        sheet.save(out/f'contact-{first//24+1:02}.jpg')
    visual=run(['ffmpeg','-hide_banner','-i',str(src),'-vf',"blackdetect=d=0.5:pix_th=0.1,freezedetect=n=-50dB:d=2,select=gt(scene\\,0.22),showinfo",'-an','-f','null','-']).stderr
    (out/'visual.log').write_text(visual)
    audio=None
    if any(s['codec_type']=='audio' for s in meta['streams']):
        audio=run(['ffmpeg','-hide_banner','-i',str(src),'-vn','-af','volumedetect,silencedetect=n=-45dB:d=1,ebur128=peak=true','-f','null','-']).stderr
        (out/'audio.log').write_text(audio)
    events=[l.strip() for l in visual.splitlines() if any(k in l for k in ['black_start:','freeze_start:','freeze_end:','pts_time:'])]
    h=hashlib.sha256()
    with src.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    report={'source_name':src.name,'sha256':h.hexdigest(),'probe':meta,'sampling_seconds':step,'sample_count':len(paths),'visual_events':events,'audio_measured':audio is not None,'audio_listened':False,'note':'Samples approximate timestamps. Logs are detections, not perceptual judgments. Inspect contact sheets and event frames.'}
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({'output':str(out),'samples':len(paths),'audio_measured':audio is not None}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('video',type=Path);p.add_argument('out',type=Path);p.add_argument('--step',type=float,default=1)
    a=p.parse_args();analyze(a.video,a.out,a.step)
