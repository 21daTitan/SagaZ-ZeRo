# Recursos disponíveis e custo

Detectar por sessão; usar `python dsant.py doctor` quando houver terminal. Verificar arquivo, rede e permissão antes de anunciar execução. Sem terminal, trabalhar com contexto e arquivos fornecidos. Não pedir senha/chave em mensagem nem incluir segredos no pack.

| Recurso | Primeiro caminho | Se ausente |
|---|---|---|
| Copy/CTA/estratégia | Modelo já acessível no aplicativo do usuário | Entregar briefing/contexto; não contratar API |
| Metadados de vídeo | yt-dlp e URL autorizada | Usar arquivo local; registrar falha de coleta |
| Quadros/cortes | FFmpeg/FFprobe; analisador local | Receber frames ou entregar plano de coleta |
| Transcrição | Legendas disponíveis; faster-whisper CPU/modelo pequeno | Receber áudio/texto; download de modelo pendente |
| Voz | Gravação própria/autorizada; TTS local já instalado | Entregar texto para gravação, sem fingir locução pronta |
| Efeitos/trilha | Síntese procedural original do módulo Cartoon | Não importar música sem autorização/licença |
| Renderização | Templates locais Remotion/Three.js, FFmpeg | Entregar projeto e comando, marcando render pendente |
| Imagens/modelagem | Ferramenta incluída na sessão, assets autorizados, Blender local | Planejar assets e manter placeholders explícitos |
| Google Flow | Só se o usuário já tiver acesso/limite adequado | Usar pipeline local ou prompts exportáveis |
| Modelo remoto | Endpoint/modelo explícitos, custo confirmado | Continuar no chat; API não é dependência do núcleo |

Perfis: core instala coordenação + Ponytail + YouTube Reverse Engineering. media acrescenta Cartoon, Remotion educativo e Storyboard Analyzer. No perfil core, não anunciar módulos de mídia como instalados; oferecer instalar perfil media ou entregar a parte textual possível.

Prioridade: aproveitar ferramentas/assinaturas existentes → recursos locais → recursos gratuitos com limites verificados → proposta paga apenas com gargalo demonstrado, custo atual e autorização. Não vender “sempre grátis”, “sempre online” ou “viralização garantida”. Hardware, energia e tráfego também limitam a execução; a VPS pequena deve começar com CPU/modelos menores e render curto de teste.

Evolução por caixa: primeiro padronizar briefing, evidência e CTA; depois medir retenção/conversas/vendas; só então propor ferramenta nova para o gargalo medido. Nunca ativar cobrança automaticamente.
