#!/usr/bin/env python3
"""Small structural regression check; doesn't claim a rendered cartoon was validated."""
import copy,datetime,json,tempfile,wave
from pathlib import Path
from plan_year import build
from validate_episode import validate
from synth_score import synth,SR
ROOT=Path(__file__).resolve().parents[1]
p=json.loads((ROOT/'assets/episode-example.json').read_text())
assert not validate(p)
for change in ['gap','state','license','cue','cost']:
    q=copy.deepcopy(p)
    if change=='gap':q['scenes'][1]['startFrame']+=1
    elif change=='state':q['scenes'][1]['state_in']={'cup':'desapareceu'}
    elif change=='license':q['assets'][0]['rights_status']='unknown'
    elif change=='cue':q['scenes'][0]['audio_cues'][0]['endFrame']=99999
    else:q['audio']['generation_cost']=1
    assert validate(q),change
r=build(datetime.date(2026,11,4))
assert len(r)==365 and r[0]['date']=='2026-11-04' and r[-1]['date']=='2027-11-03'
with tempfile.TemporaryDirectory() as tmp:
    dest=Path(tmp)/'audio';synth(p,dest)
    with wave.open(str(dest/'mix-preview.wav')) as wav:
        assert wav.getframerate()==SR and wav.getnframes()==40*SR
print('PASS: valid plan, five invalid plans, 365 dates and 40-second generated audio.')
