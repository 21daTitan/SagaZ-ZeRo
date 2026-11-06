import asyncio,json,subprocess
from pathlib import Path
import edge_tts
P=Path(__file__).parent
lines=[('FALTAVAM 5 MINUTOS','A entrega mais importante da semana. E faltavam só cinco minutos.'),('E O CARRO PAROU.','Foi quando o carro parou. Theo tentou empurrar. Mas força de vontade não liga motor.'),('O IMPREVISTO CHEGA.','Ele avisou o cliente e respirou fundo. Na próxima viagem, queria sair com um plano melhor.'),('ANTES DE PRECISAR.','Eu sou Vitor dos Santos, consultor APVS Brasil. Te ajudo a conhecer as opções e entender as condições para o seu veículo.'),('CONVERSE COM O VITOR.','Antes do próximo imprevisto, vamos conversar? Chama o Vitor no WhatsApp. O número está na tela.')]
async def main():
 result=[];start=0
 for i,(title,text) in enumerate(lines):
  await edge_tts.Communicate(text,'pt-BR-AntonioNeural',rate='+5%').save(str(P/f'public/vo{i}.mp3'))
  dur=float(subprocess.check_output(['ffprobe','-v','quiet','-show_entries','format=duration','-of','csv=p=0',str(P/f'public/vo{i}.mp3')]))
  frames=max([210,210,210,270,270][i],round((dur+1)*30));result.append({'title':title,'text':text,'start':start,'frames':frames,'voiceSeconds':dur});start+=frames
 (P/'src/data.json').write_text(json.dumps(result,ensure_ascii=False))
 print(start/30)
asyncio.run(main())
