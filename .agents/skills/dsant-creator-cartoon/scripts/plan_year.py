#!/usr/bin/env python3
"""Generate an editorial queue, not final scripts or scheduled jobs. Stdlib only."""
import argparse,csv,json,datetime
from pathlib import Path
OBJECTIVES='recuperar a chave|consertar o carrinho|conseguir sombra|entregar a encomenda|proteger a muda|reencontrar o mapa|atravessar a poça|salvar o almoço|arrumar o relógio|iluminar a oficina|limpar a lente|organizar as ferramentas|ajudar o vizinho|transportar o vidro|reparar o guarda-chuva|encher o reservatório|resgatar o brinquedo|montar a barraca|encontrar o parafuso|terminar a ponte|acertar o alarme|preparar a surpresa|recuperar o chapéu|acalmar o cachorro|desemperrar a porta|proteger o ninho|destravar a roda|carregar a bateria|entregar o presente|recuperar a placa|abrigar o visitante|montar o banco|encontrar o sinal|dividir a água|organizar a feira|pintar a fachada|proteger o desenho|recolher as peças|resgatar a bola|preparar o caminho|reparar o ventilador|guardar o estoque|encontrar o endereço|salvar a fotografia|completar o mosaico|resolver a troca|cumprir a promessa|compartilhar o prêmio|restaurar a luz|ensinar o aprendiz|preparar a festa|reunir os amigos'.split('|')
STEPS=[('Primeira pista','um caminho aparentemente fácil falha','percebe um detalhe e resolve a primeira parte','curiosidade','entretenimento'),('O atalho','a pressa cria uma consequência','contém o dano e aceita o custo','frustração','entretenimento'),('A ajuda','o outro personagem precisa de algo antes','escuta e resolve a necessidade do outro','empatia','relacionamento'),('Quase lá','o plano funciona mas revela uma limitação','descobre a causa e salva o progresso','tensão','entretenimento'),('Outra tentativa','a estratégia anterior chegou ao limite','testa uma mudança pequena e verifica o efeito','surpresa','entretenimento'),('A prova','alguém desconfia do resultado','demonstra a utilidade numa ação concreta','confiança','venda_contextual_opcional'),('O retorno','resta pagar uma promessa da semana','entrega a recompensa e recebe uma pequena ironia','alívio','relacionamento')]
def build(start=None):
    assert len(OBJECTIVES)==52
    rows=[]
    for week,obj in enumerate(OBJECTIVES,1):
        for pos,(label,obstacle,solution,emotion,mode) in enumerate(STEPS,1):
            day=(week-1)*7+pos
            rows.append({'id':f'ep-{day:03}','day':day,'arc':week,'arc_day':pos,'date':(start+datetime.timedelta(days=day-1)).isoformat() if start else None,'title':f'{label}: {obj}','desire':obj,'obstacle':obstacle,'resolution':solution,'emotion':emotion,'mode':mode,'continuity_from':f'ep-{day-1:03}' if day>1 else None,'status':'seed_unapproved','needs_specific_action':True})
    rows.append({'id':'ep-365','day':365,'arc':53,'arc_day':1,'date':(start+datetime.timedelta(days=364)).isoformat() if start else None,'title':'O objeto que ficou: final da temporada','desire':'devolver a ajuda recebida durante a temporada','obstacle':'um problema reúne as consequências dos arcos anteriores','resolution':'os amigos usam habilidades realmente adquiridas para resolver juntos','emotion':'gratidão','mode':'relacionamento','continuity_from':'ep-364','status':'seed_unapproved','needs_specific_action':True})
    assert len(rows)==365 and len({r['id'] for r in rows})==365 and len({r['title'] for r in rows})==365
    return rows
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--start',type=datetime.date.fromisoformat);a=p.parse_args()
    rows=build(a.start);a.out.mkdir(parents=True,exist_ok=False)
    (a.out/'year.jsonl').write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n')
    with (a.out/'year.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    print('365 pautas geradas; nenhuma publicação, tarefa ou render criado.')
