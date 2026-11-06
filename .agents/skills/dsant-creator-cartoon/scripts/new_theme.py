#!/usr/bin/env python3
"""Create an isolated theme and editorial queue; never overwrite existing work."""
import argparse,csv,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
options=json.loads((ROOT/'assets/production-options.json').read_text())
p=argparse.ArgumentParser()
p.add_argument('root',type=Path);p.add_argument('theme')
p.add_argument('--method',choices=options['methods']);p.add_argument('--niche',choices=options['niches'],default='livre');p.add_argument('--route',choices=options['routes'])
a=p.parse_args()
if not a.theme or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in a.theme):p.error('Use nome em minúsculas, números e hífens')
d=a.root/a.theme;d.mkdir(parents=True,exist_ok=False)
subprocess.run([sys.executable,str(Path(__file__).with_name('plan_year.py')),str(d/'calendario')],check=True)
(d/'episodios').mkdir()
(d/'personagem-e-mundo.md').write_text('# Personagens e mundo\n\nEstado: proposta; nenhum visual aprovado.\n',encoding='utf-8')
rows=[json.loads(x) for x in (d/'calendario/year.jsonl').read_text().splitlines()]
for r in rows:r.update(method=a.method,niche=a.niche,route=a.route,adaptation_required=True)
(d/'calendario/year.jsonl').write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n',encoding='utf-8')
with (d/'calendario/year.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(d/'calendario-365.md').write_text('# Calendário editorial\n\nPautas iniciais genéricas: adaptar ao nicho antes de roteirizar. Nenhum vídeo publicado.\n\n| Dia | Pauta-base | Método | Nicho | Rota | Gatilho | Status | Próximo passo |\n|---|---|---|---|---|---|---|---|\n'+''.join(f"| {r['day']} | {r['title']} | {a.method or 'a definir'} | {a.niche} | {a.route or 'a definir'} | a definir | pauta | adaptar ao nicho |\n" for r in rows),encoding='utf-8')
(d/'estado.json').write_text(json.dumps({'theme':a.theme,'method':a.method,'niche':a.niche,'route':a.route,'active_episode':None,'next_step':'adaptar pauta ao nicho, definir roteiro e método pendente','published':0},ensure_ascii=False,indent=2),encoding='utf-8')
print(d)
