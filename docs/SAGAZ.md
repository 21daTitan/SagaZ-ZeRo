# SagaZ ZERO — console ZION

Interface e execução local próprias dentro do dSantCreator. O projeto Cassandra foi examinado como referência de requisitos, mas seu código, persona, corpus de skills e camadas de evasão não foram copiados. Não foi localizado arquivo de licença no checkout consultado. O nome SagaZ identifica o aplicativo/agente, não novos pesos de um modelo.

## Iniciar

```bash
python dsant.py sagaz --web
```

Abra `http://127.0.0.1:8080`. Para outra porta: `--port 8081`. Para console: `python dsant.py sagaz`. Windows: usar `py -3` quando necessário.

A interface azul tem animação Matrix discreta, respeita movimento reduzido e adapta o layout ao celular. Console prepara tarefas; Pesquisa coleta metadados/legendas e filtra fontes; Projetos abre contextos salvos; Conexão mostra o estado real e as integrações opcionais. Nada é anunciado como instalado só por constar no catálogo.

## Modos reais

- **Local:** prepara campanha, contrato, fontes e estudos compatíveis, sem chamar modelo ou gerar roteiro final. Exporte o contexto para seu Codex, Claude, OpenCode ou chat web.
- **Modelo configurado:** opcional, requer `DSANT_BASE_URL`, `DSANT_MODEL` e chave quando necessária. Na web, marcar explicitamente “Usar modelo configurado”. No console, acrescentar `--use-model`. Pode consumir o provedor escolhido. Configuração presente não prova autorização.
- **Pesquisa YouTube:** requer yt-dlp ou evidência local. Cria `dossier.json` em rascunho; coleta não equivale a análise pronta. O agente preenche gabarito/macete e valida o resultado.

Reaproveitar endpoint Ollama ou 9Router já disponível é opcional. HTTP é permitido só em loopback; endpoint remoto exige HTTPS ou acesso por túnel. Não presumimos chave ou acesso na VPS do usuário.

## Dados e limites

Projetos ficam em `projects/sagaz/`, fora do Git. Cada tarefa recebe diretório próprio; nenhuma conversa executa shell. O servidor escuta somente em 127.0.0.1, valida origem/host e usa sessão local. Não exponha a porta diretamente na internet; para a VPS, use túnel SSH. `.env` de Cassandra não é importado ou sobrescrito.

Os contextos exportados podem conter seu briefing; compartilhe apenas com os destinos escolhidos. A interface não exibe chaves. Até duas tarefas simultâneas; um modelo externo pode aplicar limites próprios. O modo local é preparação útil, não um LLM offline embutido.

## Migração conceitual

| Cassandra de referência | SagaZ nesta entrega |
|---|---|
| CLI e web | CLI local + UI azul/Matrix |
| Provedores/API | Endpoint compatível com chat completions via núcleo existente |
| Skills em massa | Seis skills selecionadas e por tarefa |
| Execução autônoma de shell | Comandos explicitamente iniciados pelo operador; sem shell no chat |
| Persona e filtros/envelopes de evasão | Contexto atribuído e instruções de produção próprias |
| Configuração anterior | Mantida intacta; usar DSANT_* para SagaZ |

Não é cópia funcional 1:1 da Cassandra nem suporte testado a todas as suas APIs nativas. Geração real depende do endpoint escolhido. Os testes de HTTP são locais; o preview visual pelo navegador deste ambiente ficou indisponível.

## Organização 3.3

Servidor HTTP em `app.py`, preparação e continuidade em `services.py`, catálogo em `catalog.py`, interface em `index.html` e `static/`. Não há scripts embutidos no HTML. A CSP permite JavaScript e CSS apenas da própria origem.

Projetos permite retomar conversas criadas nesta versão. Cada envio cria uma versão nova com o histórico anterior; o contexto enviado ao modelo recebe as últimas oito mensagens, limitado a 24 mil caracteres. O modo local também preserva histórico, sem gerar uma resposta de LLM. Projetos antigos continuam exportáveis. Trocar de nicho requer Nova conversa.

Consulte `CASSANDRA-REVERSE-EA.md` para evidências da main de referência e o que não foi implementado.

A barra de comandos da interface está documentada em DESIGN.md. Use /help; nenhum comando do sistema é executado.

## HooLeeSh33t Matrix

`python -m sagaz serve --port 18765` abre a Matrix na raiz. O mesmo
layout atende navegador desktop e mobile. O console `python -m sagaz` usa
os comandos Matrix em texto. A interface anterior está em `/legacy`.

- `/cti [termo]` consulta a coleção local de inteligência de ameaças.
- `/criar <briefing>` encaminha copy, CTA, roteiro ou estratégia ao dSant-CreaTor.
- `python -m sagaz criar "<briefing>" --use-model` gera texto com o provedor configurado.
- Para geração no navegador, defina `SAGAZ_MATRIX_USE_MODEL=1` no ambiente
  do Core e configure `DSANT_BASE_URL` e `DSANT_MODEL`, além da chave quando exigida.
  Por padrão, o Core prepara o briefing localmente. O provedor pode cobrar por geração.

Para administração da VPS, use SSH com a sua conta de operador. Para o
GitHub, use as credenciais do Git local. A interface Matrix usa a sessão
local e os escopos existentes do SagaZ.
