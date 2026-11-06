# Duas rotas, um projeto

## Estrutura por tema

Executar `python scripts/new_theme.py RAIZ nome-do-tema`. Cada tema contém personagem-e-mundo.md, calendario-365.md, calendario/year.jsonl, calendario/year.csv, estado.json e episodios/. Cada episódio tem pasta ep-001-titulo com briefing/, roteiro/, personagens/, flow/, remotion/, audio/, referencias/, revisao/ e finais/. Guardar roteiro.md, episode.json e status.json na pasta do episódio. Criar só pastas do episódio em trabalho; não 365 pastas vazias. Usar IDs estáveis, revisão incremental e caminhos relativos no estado. Não sobrescrever pastas existentes.

Gerar 365 pautas pela ferramenta plan_year.py e calendário legível que indique pauta, rota, gatilho, status e próximo passo. Pautas não equivalem a vídeos produzidos. Atualizar o registro apenas após a etapa realmente executada. Não marcar gatilho usado/publicado só por receber exemplo. Alternar gatilhos, emoções e soluções; consultar últimas 14 entradas. Usar fila planejado → roteiro → assets → produção → revisão → pronto; publicação apenas quando solicitada. Um episódio em produção por ID, retomada pelo status, cache por hash, limite de duas tentativas do mesmo erro. Reutilizar modelos, não renders defeituosos.

## Google Flow

Preparar prompts por cena em flow/prompts.md e flow/continuidade.json. Informar início e fim, duração pretendida, identidade visual fixa, ação única principal, câmera, estado de objetos e referência ao frame final anterior. Exportar e guardar frame final de cada clipe. Gerar voz, legendas, setas e cartelas na montagem quando isso aumentar precisão. Não prometer sincronização ou consistência só porque estão no prompt; conferir nos clipes exportados.

Não presumir créditos diários, custo máximo de seis créditos, duração de clipes ou disponibilidade de modelos. Consultar a interface/documentação atual antes de gerar e registrar modelo, duração aceita, custo mostrado e saldo. Se não houver ferramenta conectada para gerar, entregar pacote pronto para colar e marcar aguardando_clipes; nunca dizer que o vídeo está pronto. Não acionar ferramenta paga substituta. Após receber clipes, verificar continuidade e montar com áudio e legendas. Flow pode ter limites e consumo; não garantir gratuidade permanente.

## Remotion

Seguir references/production.md: personagem 3D persistente, animação por frames, áudio medido, render e revisão do MP4. A rota é independente do Flow. Respeitar a direção escolhida: 2D round-head no Flow e 3D cartoon no Remotion são propostas diferentes; não converter silenciosamente. Guardar projeto reproduzível e lockfile em remotion/, MP4 em finais/.

## Referência “Faltavam 5 Minutos”

Briefing do usuário: cinco cenas de 7+8+9+8+8 = 40 s; desejo de completar entrega, alerta ignorado, pane, atraso e pergunta final; APVS no texto do post. Theo é proposta: cabeça creme, corpo fino, boné azul para trás, relógio velho no pulso esquerdo. Manter visual como proposto até aprovação explícita; não exigir aprovação para organizar documentos.

Corrigir causalidade antes de produzir: definir o que está sendo entregue e quem saiu; mostrar como o relógio rachou na queda; explicar como o carro chegou ao portão depois da pane; plano B deve aparecer como possibilidade concreta. Assistência não substitui manutenção nem garante prazo de entrega; só apresentar benefício APVS confirmado na campanha. Evitar alegação absoluta “está em todo lugar” sem fonte. CTA fornecido pelo usuário: @21apvs e (21) 99879-3765; registrar origem e confirmar ao publicar. Persuasão por consequência e alternativa real, sem garantir cobertura contratual. Numerar gatilhos somente com catálogo definido; nº7 é a etiqueta do exemplo, não uma taxonomia universal.

## Retomada

Ler estado.json, personagem-e-mundo.md, calendário e status do episódio antes de agir. Registrar arquivos, decisões, rota, pendências, próximo passo e autorização real. Se o usuário trocar de rota, preservar trabalho e abrir nova revisão. Não criar automação diária sem solicitação de agendamento.
