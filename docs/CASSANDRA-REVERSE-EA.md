# Engenharia reversa da Cassandra → SagaZ 3.3

Origem: https://github.com/DarkyHArry/cassandra-agent/tree/9c7bfba7a66df184de70904c2d87acc45aec0eaa

Revisão local analisada: `9c7bfba7a66df184de70904c2d87acc45aec0eaa`. A consulta `git ls-remote origin refs/heads/main` confirmou essa revisão na branch main durante o trabalho. Este é um estudo de implementação e contratos; não foi executada a Cassandra nem seu corpus de skills.

## Mapa observado

| Área | Evidência no upstream | Decisão no SagaZ |
|---|---|---|
| Entrada CLI | agent.py, classe Agent e inicialização | Conservar dsant.py como entrada pública e CLI SagaZ |
| Transporte | cassandra/client.py | Reutilizar nosso creator.py / run, sem duplicar transporte |
| Provedores | cassandra/providers.py; web_ui.py /api/providers e /api/models | Metadados de conexão isolados em catalog.py; somente protocolo compatível já implementado |
| Skills | agent.py / load_available_skills e get_relevant_skillogy | Catálogo dinâmico das seis skills em /api/skills; seleção de procedimento continua no núcleo |
| Contexto | cassandra/compact.py; Agent.clear_session | Conversas persistidas e retomáveis, com últimas oito mensagens e até 24 mil caracteres no contexto |
| Web | web_ui.py / HTML_CONTENT e endpoints | HTML, CSS, JS e serviço de tarefas em arquivos separados |
| Credenciais | web_ui.py / CredentialRequest e /api/credentials | Variáveis DSANT_*; a UI recebe presença da chave, nunca seu valor |
| Estado real | web_ui.py /api/status | Conexão configurada e acesso verificado são estados diferentes |
| Execução | agent.py / execute_shell_blocks | Mantida fora do chat; procedimentos executados explicitamente pelo operador |

## Fluxo reconstruído e adaptado

Entrada → validação → seleção de procedimento → montagem de contexto → preparação local ou chamada explícita de modelo → persistência → resposta e exportação.

O principal mecanismo reaproveitável é a separação entre identidade do agente, seleção de capacidade e transporte. O modelo é substituível; skills e histórico pertencem ao aplicativo. Esse desenho permite preservar os mesmos projetos em Codex, Claude e OpenCode sem prometer equivalência entre ferramentas dessas plataformas.

## Organização entregue

| Caminho | Responsabilidade |
|---|---|
| dsant.py | Instalação, atualização, diagnóstico e comandos públicos |
| sagaz/app.py | HTTP, sessão, validação de host/origem e limites |
| sagaz/services.py | Preparação, pesquisa e continuidade entre versões |
| sagaz/catalog.py | Metadados de skills e conexão sem segredos |
| sagaz/index.html | Estrutura sem scripts ou estilos embutidos |
| sagaz/static/app.css | Identidade azul/Matrix, alinhamento e celular |
| sagaz/static/app.js | Navegação, envio, retomada e exibição segura |
| .agents/skills/ | Fontes das seis skills e seus assets |
| knowledge/ | Catálogos e estudos atribuídos |
| docs/ | Contratos, decisões e validação |
| tests/ | Verificações offline |
| projects/, state/, exports/ | Dados locais fora do Git |

## Cobertura e limites

Implementados: interface modular, navegação por função, catálogo real das skills, metadados de conexão, histórico retomável, continuidade de contexto e versões imutáveis. A troca de nicho exige conversa nova para impedir mistura entre APVS, RR e adulto.

Não implementados nesta revisão: streaming de tokens, APIs nativas de 18 provedores, catálogo remoto de modelos, rotação de credenciais ou resumo por modelo. O contexto é truncado de forma explícita, não resumido. A resposta usa texto seguro, sem renderização Markdown executável. O histórico mantém até 40 mensagens por versão; os arquivos anteriores permanecem intactos.

## Origem e licença

Não foi encontrado LICENSE/COPYING na raiz da revisão consultada. Há licenças específicas em alguns subdiretórios de skills, que não estabelecem licença para o restante do projeto. O SagaZ continua uma implementação independente, inspirada na organização e nos contratos observáveis. Não redistribuímos código, persona ou corpus Cassandra. HooLeeSheet não se torna um fork nativo do GitHub por usar uma referência externa.
