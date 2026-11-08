# Memória Discord

O módulo `sagaz.discord_memory` é um armazenamento SQLite local para mensagens de canais autorizados. Ele não usa token de usuário nem faz scraping de cliente. A leitura do histórico deve ocorrer por um bot oficial com `Read Message History` e `Message Content Intent` aprovados no servidor.

Fluxo offline:

```bash
python3 -m sagaz discord ingest mensagens.json --consent
python3 -m sagaz discord stats
python3 -m sagaz discord search "termo"
```

O JSON é uma lista com `id`, `channel_id`, `author_id`, `author_name`, `content` e, opcionalmente, `timestamp`, `reply_to`, `attachments` e `reactions`. A opção `--consent` é obrigatória para impedir ingestão acidental.

O MCP expõe somente `sagaz_discord_summary` e `sagaz_discord_search`, ambos read-only. A ingestão permanece fora do MCP até existir um conector oficial com escopo de servidor/canal, retenção e opt-out definidos.
