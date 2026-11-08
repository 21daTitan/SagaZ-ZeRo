# SagaZ-ZeRo — Operator V4

Objetivo: visual de terminal próprio e conversa **real** via modelo OpenAI-compatible, mantendo CTI, MCP e a interface HooLeeSh33t. A implementação não usa código ou imagens copiados da Cassandra.

## Comandos

- `sagaz` inicia a TUI com comandos legíveis e respostas reais depois de configurar o provedor.
- `/conectar` salva `~/.config/sagaz-zero/provider.json` com permissões 0600 no **usuário que executa `sagaz`**. A chave não aparece no terminal. A configuração pode implicar cobrança pelo provedor.
- `/testar` faz uma chamada real, possivelmente cobrada. Sem provedor configurado, informa precisamente a pendência.
- `/cti [termo]`, `/skills`, `/status`, `/modelo`, `/limpar`, `/ajuda` e `/dsant` são locais.
- `sagaz --web --port 8080` inicia a interface; endpoint `/api/matrix/chat` usa IA quando configurada, salvo `SAGAZ_MATRIX_USE_MODEL=0`.
- `dsant` é somente um conector reservado, sem execução. O comando legado `/criar` continua por compatibilidade, mas não é o fluxo principal.

## Segurança e limites

- Somente HTTPS remoto, ou HTTP localhost. Chaves salvas em arquivo local 0600; não versionar.
- O código do chat usa o Gateway existente (auditoria e limites de custo, quando configurados).
- O cache é histórico local versionado (não um banco vetorial ou agente autônomo); 12 mensagens anteriores entram no contexto e até 40 ficam no arquivo. Não promete 128k tokens nem execução de shell.
- `/testar` comprova resposta do provedor, não desempenho nem disponibilidade permanente.
- Não exponha a interface HTTP diretamente à internet sem autenticação adicional e TLS. Prefira túnel SSH.
- Backup de cada arquivo modificado: `state/backups/sagaz-operator-v4-*`.
- O `apply.py` reverte em caso de falha de testes. Não publica GitHub nem reinicia serviços.

## Fluxo GitHub + VPS

Criar branch a partir da `main`, executar `python3 apply.py --repo . --dry-run`, `python3 apply.py --repo .`, revisar diff, subir branch, validar GitHub Actions e fazer merge. Na VPS atualizar por release versionada, manter rollback e testar `/healthz`, `/api/cti/summary`, UI e uma resposta de IA. Nunca ativar deploy só pelo status do commit.
