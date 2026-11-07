# Integração ALFA-CTI → SagaZ-ZeRo

Referência de projeto: `21daTitan/SagaZ-ZeRo`, branch de UI `feature/hooleesh33t-blue-matrix-v1`.

O serviço original é mantido. O módulo CTI acrescenta somente consulta local e leitura via MCP; não inicia ferramentas de ataque.

- UI existente: terminal `/cti <termo>` (não substitui HTML ou CSS).
- API autenticada: `GET /api/cti/search?q=FIN7&limit=10`.
- MCP autenticado: `sagaz_cti_search` (argumentos `query` e `limit`).
- Coleção: 10 registros `ALFA-CTI-0011` a `0020`, importados como alegações não verificadas.
- Lote 1: não importado; arquivos não disponíveis.
- Cassandra: nome do produto para operador é `SagaZ-ZeRo`, mantendo crédito original upstream onde apropriado; não renomear nomes de pacotes Python, URLs e referências históricas indiscriminadamente.
- Fontes ChatGPT: links de projeto/compartilhamento fornecidos em 2026-11-06 não puderam ser lidos por conectores; não considerá-los ingeridos.

## Verificação

`python -m unittest tests.test_cti -v`
`python -m unittest discover -s tests -v`
`python dsant.py doctor`

## Publicação

Integrar por Pull Request com revisão dos testes. Na VPS, executar backup, deploy de staging, healthcheck e rollback; a publicação do código no GitHub não significa instalação na VPS.
