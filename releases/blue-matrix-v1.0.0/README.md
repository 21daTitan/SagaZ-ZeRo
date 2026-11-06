# HooLeeSh33t — SagaZ-ZeRo by dSant

**Blue Matrix v1.0.0 · pacote de integração não destrutiva**

Sistema original by dSant (`@21daTitan`). A marca principal é **SagaZ-ZeRo / HooLeeSh33t**; **dSanT-CreaTor** é um setor independente e extensível.

## Funciona agora

- Interface responsiva Matrix azul para **chat, conexões, comandos, anexos e estudos**.
- Análise local de arquivos de texto (prévia, até 1 MB) e exportação local de notas.
- dSanT-CreaTor com **pedido livre**, modo guiado opcional, 2D/3D/UGC, duração, formato, roteirização, CTA, prompt mestre, sugestões e exportação JSON/TXT.
- Servidor Python sem dependências externas para a Web UI e **chat autenticado opcional** via API de chat compatível com formato OpenAI (configurada no servidor).
- Publicação segura em branch separada e implantação de **prévia** na VPS, sem mexer no Core ativo.

## Não é entregue nesta versão

- Controle direto de outros agentes ou ferramentas de terminal; telas correspondentes são especificações/previews, **não execução**.
- Renderização de vídeo/MP4, utilização real de créditos OmniFlash ou integração comprovada ao Google Flow.
- Upload de anexos para IA, memória sincronizada entre dispositivos, login multiusuário/BYOK, integração nativa GitHub/Notion, pagamentos ou mineração.
- Migração automática, desinstalação ou substituição do Core já existente. **Não apague o sistema em produção.**

## Executar no Termux, Linux ou VPS (prévia local)

```sh
python3 server/sagaz_server.py
```

Abra **http://127.0.0.1:8765/** (SagaZ) ou **http://127.0.0.1:8765/creator** (dSanT-CreaTor).

O chat mostra **Core: prévia** até você configurar as variáveis de ambiente. Nenhuma chave deve ser colada no JavaScript ou publicada no GitHub.

## Habilitar chat real (somente ambiente seguro e privado)

```sh
export SAGAZ_API_KEY='COLE_SUA_CHAVE_NO_SEU_TERMINAL'
export SAGAZ_ADMIN_PASSWORD='CRIE_UMA_SENHA_LONGA_E_UNICA'
export SAGAZ_SESSION_SECRET="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
export SAGAZ_UPSTREAM_URL='https://api.openai.com/v1/chat/completions'
export SAGAZ_MODEL='gpt-4.1-mini'
python3 server/sagaz_server.py
```

Requer uma chave válida, com saldo e acesso ao modelo. Cada chamada pode gerar cobrança do provedor. **Não copie os valores reais para arquivos versionados.** Para acesso externo configure HTTPS e `SAGAZ_COOKIE_SECURE=1`, além de reverse proxy seguro e autenticação reforçada. O servidor escuta apenas `127.0.0.1` por padrão.

O backend inclui autenticação por cookie de sessão, proteção de requisições, limites de tamanho, política de conteúdo e conversa temporária em memória. Não substitui um gateway multiusuário de produção.

## Publicar sem sobrescrever a instalação existente

Execute `bash scripts/publicar_github.sh` a partir desta pasta. O script clona a branch padrão do repositório e cria `feature/hooleesh33t-blue-matrix-v1`. As pastas são adicionadas sob `releases/blue-matrix-v1.0.0/` para evitar conflito com o Core instalado. Faça revisão antes do merge.

## Testes

```sh
python3 -m unittest discover -s tests -v
node --check apps/hooleesh33t-matrix-v1/app.js
node --check apps/dsant-creator-v1/app.js
```

Leia `docs/STATUS.md`, `docs/ARQUITETURA.md`, `docs/SEGURANCA.md` e `docs/MIGRACAO_VPS.md` antes de colocar a versão em domínio público.
