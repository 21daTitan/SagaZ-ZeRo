# 365 dias com continuidade

Executar `python scripts/plan_year.py DIRETORIO_NOVO [--start YYYY-MM-DD]`. Sem data informada, gerar dias 001–365 sem inventar calendário. O resultado é fila de 365 pautas distintas, não 365 roteiros finalizados ou vídeos. 52 arcos de sete episódios = 364; dia 365 fecha a temporada. A produção diária não é agendada pela instalação.

Arco semanal: desejo/primeiro obstáculo, solução apressada, ajuda/empatia, pressão/objeção, mudança de estratégia, demonstração de resultado, payoff da semana. Cada episódio resolve um subproblema, inclusive quando deixa continuação. Manter consequência: o objeto obtido no dia 1 continua existindo no dia 2, salvo perda mostrada.

Roteirizar lote de 7, produzir animatics, aprovar o que a autorização ainda não cobre, produzir os renders e guardar reserva de 3–7 episódios. Não aprovar 365 versões automaticamente. Trabalhar com cenários/props reaproveitados e variar conflito, encenação e solução. Se animação custar demais, reduzir props/figurantes e renderizar mais devagar, preservando a ação central e o 3D pedido.

Operação por episódio: consultar bíblia e últimas 14 pautas → escolher desejo e conflito não repetidos → escrever final primeiro → preparar gancho → avaliar continuidade → animatic → áudio → render → QA → registro → entrega. Máximo duas novas tentativas automáticas por erro idêntico; depois registrar blocked com diagnóstico.

Registro `episodes.jsonl`: id, day, title, premise, desire, obstacle, solution, emotional_turn, canon_version, state_before, state_after, asset_hashes, output_hash, status, published_at (somente se publicado de fato), métricas com fonte e data. Não armazenar o registro mutável dentro da instalação da skill; salvar com o projeto da série. Não gerar duas vezes um id complete sem pedido de revisão; usar revision incremental.

Quando existir publicação autorizada, separar upload de publish. Consultar ferramentas e termos atuais; não assumir que a skill tem credenciais, que ChatGPT executará render pesado em horário fixo ou que pode enviar para contas sem conexão.
