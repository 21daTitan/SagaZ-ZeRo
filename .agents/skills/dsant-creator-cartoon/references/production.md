# Pipeline concreto — mesma base do painel

## Proveniência técnica

Inspecionado `rr-3d-painel-v2.zip`, projeto 40 s, 1080×1920, 30 fps. A fonte usa Remotion 4.0.540, React 19.2.0, Three 0.180.0, R3F 9.4.0, TypeScript 5.9.3; cenas contíguas, câmera por chaves, modelo 3D persistente, palavras temporizadas, áudio composto em Python/NumPy/SciPy/SoundFile, FFmpeg e render Chromium swangle. Voz do painel: pt-BR-AntonioNeural via edge-tts, +2% e ajuste posterior 1,06×. Isso documenta aquele projeto, não um preset obrigatório para todos.

`assets/panel-reference` preserva fontes e scripts locais úteis. Não inclui mídias binárias, fontes externas, node_modules, chave API nem o gerador com alternativa paga. Não é um cartoon pronto nem pacote autossuficiente de reprodução do painel: para reconstruir literalmente aquele vídeo, usar o ZIP original com mídias. Para um cartoon novo, usar código como referência, gerando seus próprios assets/dados.

## Pré-voo

1. Verificar Node, Python, ffmpeg/ffprobe, RAM, navegador e dependências instaladas antes de instalar. Não atualizar dependências por impulso. Copiar a base para pasta nova do episódio e criar lockfile ao instalar, guardando versão real de ferramentas.
2. Usar os pacotes fixados do `package.json` como ponto de partida e declarar explicitamente `@remotion/bundler`/`@remotion/renderer` na mesma versão 4.0.540, pois render.mjs os importa. Usar navegador local via CHROME_BINARY quando necessário. Avaliar qualquer compatibilidade com Node a partir do ambiente real, não só do README histórico.
3. Começar com 1 processo em máquina de 1 vCPU/4 GB, preview 540×960, sombras reduzidas. Medir 60 frames antes de estimar lote. Render final 1080×1920 em blocos se necessário; não prometer tempo sem benchmark.
4. Não disparar APIs pagas, jobs externos nem compras. Remotion tem licença gratuita condicional: uso individual/equipe pequena conforme termos atuais. Fonte oficial consultada em 04/11/2026: https://www.remotion.dev/docs/license/pricing e https://www.remotion.dev/docs/terms . Rever se tamanho/uso mudar. Não chamar Remotion de software livre irrestrito.

## Sequência de produção

A. Roteiro: salvar episode.json e tabela com tempo, intenção, ação, câmera, estado, texto, áudio e gag. Definir um objeto causal e plano de payoff. Registrar limites ainda pendentes.
B. Bíblia: definir modelos únicos e rig. Aprovar visual conforme autorização existente; usar novo cânone versionado se usuário aceitar mudança. Reutilizar meshes/materials, não recriar por plano.
C. Voz: usar gravação autorizada ou serviço gratuito disponível. Se usar Edge: `edge-tts --voice pt-BR-AntonioNeural --text 'texto aprovado' --write-media fala.mp3 --write-subtitles fala.vtt`; confirmar opções na versão local. VTT pode ter granularidade de frase: não alegar palavra a palavra sem boundaries reais. Preservar limites medidos; se houver time-stretch, multiplicar TODOS os tempos por fator inverso. Texto da legenda = fala real.
D. Timing: derivações de voz final ou de atuação quando sem narração; frames inteiros, estados completos. O episódio de exemplo é de atuação, sem TTS obrigatório. Guardar tempos estimados separados dos medidos.
E. Mundo: substituir World.tsx por personagem/ambiente originais. Geometria real, iluminação suave, sombras de contato e profundidade clara. Não apresentar cartelas movendo como 3D. Reutilizar CameraController, helpers de interpolação, captions e contratos quando compatíveis. Eliminar títulos RR, WhatsApp, logotipo, fonte RR e objetos automotivos se não fizerem parte do episódio.
F. Determinismo: tudo deriva de frame; não usar Date.now, setInterval, física dependente de tempo real ou Math.random não semeado. Simulação deve ser pré-calculada ou analítica. Dentro de Sequence, frames locais; para estado persistente, usar frame global coerente.
G. Áudio: construir stems voice/music/sfx separados. `scripts/synth_score.py` gera cama original e cues simples por frame com seed fixa; resultado é rascunho funcional, não trilha cinematográfica garantida. Mixar ducking sob fala com rampas, reservar silêncio expressivo; guardar cue sheet. Usar scripts/loudnorm.py e audiocheck.py do painel como referência.
H. Render: adaptar Root.tsx e render.mjs ao novo compositionId, duração e output. Não deixar 1200 frames e RRPainel hardcoded se o novo episódio difere. Rodar tsc/lint, stills e revisar antes do render completo. Usar scripts padrão do projeto, verificar processo concluído e arquivo.
I. QA: FFprobe de streams, detecção de black/silence/freeze, imagens no MP4 final e validação de cena/cânone. blackdetect pode marcar cenas noturnas legítimas: revisar visualmente; toda cauda preta inesperada >0,5 s bloqueia. Freeze pode ser pausa cômica legítima: revisar intenção, não apagar automaticamente.
J. Persistência: salvar projeto sem node_modules, lockfile, assets autorizados, roteiro, episode.json, bíblia, status, relatório, arquivos de voz e final. Registrar hashes. Não sobrescrever episódio anterior. Reusar caches por hash sem vazar mídias entre personagens.

## Áreas de quadro

Para 1080×1920, começar com conteúdo crítico entre x=90–990 e y=240–1540. Legenda até 2 linhas de cerca de 24 caracteres, fonte de licença verificada; medir na tela pequena. Usar fontes do sistema como fallback e registrar mudança. Não redistribuir OpenAI Sans do painel sem verificar permissão. Separar rosto, legenda e botão; proporção e legibilidade vencem ornamentação. Nenhuma margem é garantia universal para toda interface de plataforma.

## Estado operacional

`production-status.json`: episode_id, fase (planned/animatic/rendering/qa/complete/blocked), arquivos, autorizações reais, verificações executadas, pendências e próximo passo. Não guardar segredos. Skill não aumenta recursos de computador nem roda sozinha. Integração de agendamento é separada, com retry limitado, idempotência por episode_id e zero publicação automática sem autorização.

## Verificações desta instalação

Executados: quick_validate; contrato do episódio exemplo; cinco casos inválidos (lacuna, estado, licença, cue e custo); geração de 365 pautas com datas contíguas; síntese local de 40 s; analyze_video sobre o MP4 enviado. Código-fonte do painel foi inspecionado, mas nenhum novo cartoon foi renderizado nesta criação da skill. Audio da referência e da playlist não foi ouvido.
