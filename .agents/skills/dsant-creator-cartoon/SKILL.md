---
name: dsant-creator-cartoon
description: Criar shorts narrativos 3D do dSanT Creator Cartoon com humor físico, drama, escolhas, persuasão ética e continuidade diária. Usar para engenharia reversa de vídeo de referência, criar episódios/cartoon original, planejar 365 dias, incorporar playlist como referência musical ou produzir/renderizar histórias com o método gratuito do painel RR (Remotion, Three.js, áudio por código), com escolha entre Google Flow e Remotion, métodos cartoon, 3D cinematográfico e automotivo técnico/POV; nichos APVS, automotivo e hot adulto não explícito; organização automática por tema e calendário. Sem Runway. Skill independente da skill educativa de mecanismos.
---

# dSanT Creator Cartoon

Trabalhar em português brasileiro, com comunicação curta e produção cuidadosa. Tratar esta skill como procedimento e memória externa consultável, não como treinamento permanente do modelo. Manter tudo isolado; não modificar a skill educativa nem o projeto do painel.

## Começar pelo estado real

1. Ler `references/reference-analysis.md` para entender o vídeo analisado e seus limites. Ler `references/story-direction.md` para narrativa, interpretação e persuasão.
2. Encontrar a pasta da série e ler `series-bible.json`, `episodes.jsonl`, `production-status.json` e o último episódio aprovado. Na ausência, inicializar a partir de `assets/series-bible.json`. A proposta de elenco ali NÃO é cânone aprovado.
3. Ler `references/production.md` antes de gerar vídeo; usar `assets/panel-reference/` como fonte técnica local. Esse código vem do painel real, contém identidade RR e caminhos de mídia antigos: é referência, não um novo cartoon pronto. Adaptar personagens, cenário, dados, duração e áudio em uma pasta de produção separada.
4. Não depender da outra skill instalada, dos antigos caminhos de scratch, de APIs pagas ou do vídeo original para entender o método. As referências e o código essenciais estão neste pacote.
5. Para novo vídeo enviado, executar `python scripts/analyze_video.py VIDEO DIRETORIO_NOVO`; inspecionar todas as folhas de contato, depois frames em torno de cada evento e corte. Distinguir observado, medido, inferido e não verificado. Inspecionar toda a duração, inclusive cauda preta. Nunca inferir software gerador, prompt, voz, fonte, BPM ou movimentos exatos a partir de pixels insuficientes.

## Definir o entregável

- Pedido de análise: entregar decomposição temporal e regras transferíveis; não prometer clonagem perfeita.
- Pedido de roteiro: entregar história completa com planos, ações e final.
- Pedido de vídeo: planejar, implementar, renderizar e revisar até entregar MP4. Se o usuário já autorizou produção, não exigir confirmação redundante. Resolver escolhas reversíveis; pedir somente decisão realmente ausente que impeça a produção. Não aplicar automaticamente a pausa da skill educativa.
- Pedido de série: planejar 365 pautas e trabalhar em lotes de sete. Não confundir pautas com roteiros prontos nem planejamento com 365 renders.
- Pedido explícito de execução diária futura: usar Automations se disponível e esclarecer o horário se necessário; não afirmar que instalar a skill cria um serviço em segundo plano. Não agendar/publicar só porque a meta editorial é diária.

## Padrão de episódio

Escolher método e nicho pelo pedido, consultando `references/methods-and-niches.md` e `assets/production-options.json`. O método 3D cinematográfico é opcional, não um novo padrão universal. Adotar 35–45 s, 1080×1920, 30 fps; adaptar a direção ao método selecionado, sem impor geometrias simples a pedidos detalhados. Um desejo concreto, dois obstáculos causais, uma virada e uma pequena resolução. Variar entre comédia, ternura, tensão e surpresa. Usar drama sem sofrimento gratuito e sem fórmulas que prometam “dopamina” ou viralização.

- Mostrar a ação/problema nos primeiros 0,4–1 s; nada de logo ou saudação antes da história.
- Organizar: desejo → tentativa → custo → tentativa diferente → aparente derrota → descoberta → recompensa/ironia.
- Preservar espaços de leitura e reação. Alternar plano amplo, detalhe do objeto e rosto/corpo reagindo. Não mover câmera continuamente por regra.
- Fazer cada corte mudar informação, intenção, posição ou risco. Evitar zoom aleatório e excesso de texto.
- Resolver algo no episódio antes de abrir outra pergunta. Votação é opcional; quando houver, opções devem produzir consequências diferentes e a decisão precisa ser cumprida depois. Não inventar votos reais.
- Não copiar o personagem Henry, o desenho Oscar, cenários, diálogos, música ou cenas plano a plano. Absorver desejo simples, perseguição espacial, antecipação, erro e reação; criar elenco e mundo originais.
- Usar as referências de livros como lentes criativas do usuário, não como citações ou resumos supostamente fiéis. Não inventar autores, trechos, números de vendas ou promessas comerciais.

## Continuidade e contrato

Produzir `episode.json` usando `assets/episode-example.json` como contrato explícito. Todos os planos precisam de início/fim em frames inteiros [startFrame,endFrame), ação, câmera, emoção, narração, estado inicial/final e som. Atualizar estado somente quando a ação o justificar. Identificar teleporte, elipse ou reset deliberado como transição.

Travar no cânone: escala, proporções, paleta, marcas, rig, voz, relações, desejos, limites físicos e objetos recorrentes. Guardar `canon_version`, seed e hashes dos assets. Não regenerar personagem por plano. Usar o mesmo mesh/rig com poses diferentes. Verificar também direção do olhar, mão que segura o objeto, sujeira, dano, estoque e geografia do cenário.

Rodar `python scripts/validate_episode.py episode.json`. Validar contiguidade, soma, narrativa mínima, transições de estado, uso de assets com licença conhecida e áudio dentro dos limites. Validar o episódio anterior com a bíblia; o script não substitui essa leitura.

## Produção sem cobrança por geração

Usar geometria procedural, Remotion + React Three Fiber/Three.js, FFmpeg, áudio sintetizado local e voz própria/gravação autorizada. Narração é opcional se a atuação conta tudo. Se houver locução, gerar antes de travar cortes, medir os arquivos e alinhar palavras; não usar tempos estimados como alinhamento final. Edge TTS é opção sem cobrança direta observada no painel, dependente de rede/serviço; não é garantia de acesso perpétuo. Se indisponível, usar voz gravada ou TTS local com licença verificada; não entregar vídeo sem a voz prevista fingindo estar completo.

Ler `references/music.md` ao receber a playlist. A playlist do usuário já está catalogada em `references/playlist-reference.json` (71 títulos/artistas; áudio não ouvido). Usar status `metadata_only` até analisar áudio; não dizer que a referência está ausente. Usar trilha procedural original provisória conforme direção proposta em music.md. Não baixar ou usar músicas da playlist como se referência fosse licença.

Não chamar Runway nem ferramentas de mídia paga. Conferir elegibilidade/licenças antes de escalar; “sem taxa de geração” não elimina custo de equipamento, energia, internet e plano já contratado. Verificar condições atuais se equipe/uso mudar.

## Revisar e aprender

- Executar TypeScript/lint e validar dados. Renderizar início, antecipação, contato/impacto, reação e fim de cada cena, além dos dois lados dos cortes.
- Examinar o MP4 final, não só imagens do projeto. Bloquear cauda preta inesperada, frame vazio, atravessamentos, personagem diferente, objeto surgindo do nada, legenda ilegível e fala cortada.
- Medir duração, frames, resolução e áudio com FFprobe/FFmpeg. Meta inicial de áudio: −14 LUFS integrados e true peak ≤ −1,5 dBTP, verificando após a codificação. Isso é alvo de trabalho, não exigência universal de plataforma.
- Ouvir quando houver ferramenta capaz. Sem audição, declarar “medido; avaliação auditiva pendente”; não adivinhar timbre/ritmo da referência.
- Aplicar `references/quality-learning.md`. Registrar métricas reais quando fornecidas; alterar uma hipótese por experimento, preservando o cânone. Não afirmar aprendizado com métricas inexistentes.
- Entregar MP4, projeto reproduzível, roteiro e status honesto. Persistir artefatos pela ferramenta de arquivos disponível. Marcar concluído só após arquivo final e verificações; publicação exige pedido próprio.

## Recursos

- `references/reference-analysis.md`: decomposição do vídeo enviado, medições e limitações.
- `references/story-direction.md`: drama, atuação e persuasão em ações.
- `references/production.md`: método do painel e adaptação para cartoon.
- `references/music.md`: playlist, assinatura sonora e direitos dos assets.
- `references/year-plan.md`: 52 arcos × 7 dias + final; gestão de fila.
- `references/quality-learning.md`: critérios de aceite e experimentos.
- `assets/series-bible.json`, `assets/episode-example.json`: estado e contrato concretos.
- `assets/panel-reference/`: fontes técnicas do painel, sem áudio/fontes externas; não executar sem adaptação.
- `scripts/analyze_video.py`: sondagem, amostragem, cortes e áudio medido.
- `scripts/plan_year.py`: 365 pautas numeradas, distintas e não aprovadas.
- `scripts/validate_episode.py`: validação estrutural antes da produção.
- `scripts/synth_score.py`: trilha/efeitos originais locais a partir de cues.


## Rotas de produção e organização obrigatória

Ler `references/routes-and-workspace.md` antes de iniciar um tema ou episódio. Oferecer Google Flow e Remotion; se o usuário já escolher, executar a rota escolhida. Usar Remotion como padrão local quando não houver preferência. Não tratar o roteiro “Faltavam 5 Minutos” como vídeo já renderizado nem como cânone aprovado. Criar a pasta do tema com `scripts/new_theme.py`; salvar calendário e estado fora da instalação desta skill. Preservar todos os episódios anteriores.


## Métodos e nichos independentes

Ler `references/methods-and-niches.md` ao escolher ou trocar o formato. Registrar separadamente `method`, `niche` e `route` no estado e no contrato do episódio. Usar `scripts/new_theme.py RAIZ TEMA --method cinematic-3d --niche apvs --route remotion` para organizar um tema; consultar `--help` para outras opções. Preservar chamadas antigas sem opções. Não importar nomes, contatos, personagem ou textos comerciais de outro nicho. A escolha do 3D detalhado em um vídeo não aprova permanentemente Theo nem os demais assets.

Fontes técnicas locais disponíveis: `assets/cinematic-reference/` (revisão APVS em 3D detalhado com ambiente sonoro) e `assets/panel-reference/` (modelo do painel RR do outro chat). São fontes de adaptação, não pacotes completos com dependências, fontes, voz e trilha incluídas. Ver `references/automotive-model.md` antes de usar o modelo automotivo. Não marcar exemplos renderizados como aprovados pelo usuário sem aprovação explícita.


## Acabamento opcional de curta

Ler `references/shorts-style.md` para personagens 2D em mundo 3D. Usar os templates MIT em `assets/shorts-reference/` apenas após adaptação; não importar frames privados de estudo nem preferências de idioma do autor.
