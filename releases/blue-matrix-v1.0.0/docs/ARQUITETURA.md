# Arquitetura e sincronização

## Identidade do produto

`SagaZ-ZeRo` = agente operacional principal e individual, com identidade própria.
`HooLeeSh33t` = sua interface web operacional.
`dSanT-CreaTor` = setor independente especializado em produção multimídia e extensível a novos fluxos.

## Topologia pretendida

```text
                    HooLeeSh33t Web UI
                             |
                       SagaZ Core API
                             |
       +---------------------+-----------------------+
       |                     |                       |
  Gateway de IA        Orquestrador             Cofre de dados
  por provedor         de agentes               e memória
       |                     |                       |
  OpenAI/Claude...      Termux/VPS/etc.         projetos/estudos
                             |
                    Eventos versionados
                             |
                    dSanT-CreaTor API
                             |
                    Planejamento -> Geração
```

## Contratos estáveis

- API v1: `GET /api/v1/status`, `POST /api/v1/chat`, `POST /api/v1/chat/reset` (implementação básica), `POST /api/v1/login` (single-admin).
- Em integração futura, `POST /api/v1/files` fará uploads autenticados e inspeção segura; **ainda não existe**.
- Operações críticas exigem **prévia + aprovação humana + auditoria**. Não aceite shell bruto vindo do navegador.
- Comunicação entre setores é proposta via `event envelope` com `schema_version`, `event_id`, `trace_id`, `issuer`, `scope`, `payload` e `approval`. Esquema de referência em `docs/contracts/event.schema.json`.
- Memórias e projetos compartilhados precisam de segregação por usuário e permissões, sem transportar segredos para clientes.
- Cada integração deve declarar capacidade, autorização, versão e comportamento na ausência do provedor.

## Política de mudanças

1. Inventariar a instalação existente sem desligar serviços.
2. Backup e checksum antes de migrar qualquer arquivo.
3. Branch feature e PR; não substituir `main` sem revisão.
4. Testes de contrato, regressão, segurança e rollback.
5. Migração em paralelo/canário, só depois troca de tráfego.
6. Remover versões antigas apenas após aprovação explícita e backup recuperável.
