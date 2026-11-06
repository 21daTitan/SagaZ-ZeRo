# Contratos operacionais da versão 3.3.0

Esta especificação foi escrita a partir do código desta entrega. A ideia de rastrear implementação → contrato → teste usa Reversa como referência de processo; o pacote Reversa não foi instalado.

| Área | Fonte | Contrato | Verificação |
|---|---|---|---|
| Instalação | dsant.py / install | Não sobrescrever terceiros/edições; backup de versão gerenciada | test_setup.py |
| Atualização | dsant.py / update | Origin conhecido, árvore limpa, somente avanço simples | test_setup.py com Git local |
| Campanha | creator.py / prepare | Pasta nova, nicho/método/rota explícitos, notas por escopo | testes do núcleo e playlist |
| Modelo | creator.py / run | Endpoint explícito, HTTPS remoto, chave fora do contexto | transporte simulado; sem chamada paga |
| YouTube | reverse.py / acquire | Vídeo canônico ou legenda local, dados/profundidade preservados | VTT/JSON3 locais e URLs inválidas |
| Dossiê | reverse.py / validate | Notas avaliáveis, média/cobertura, limites e evidência por modalidade | test_reverse.py e teste independente |
| SagaZ HTTP | sagaz/app.py | Loopback, sessão local, origem/host, corpo limitado, sem shell | test_sagaz.py |
| SagaZ UI | sagaz/index.html e static/ | Dados não confiáveis via textContent; opção de modelo desmarcada | sintaxe JS; revisão visual pendente |

Fluxo: usuário define briefing → prepare cria campanha/contexto → operador usa agente do aplicativo ou seleciona endpoint → resultado passa por revisão → render só quando o pipeline multimídia for executado. Nenhum desses passos implica publicação.

Dados persistentes: projects/, state/ e exports/ são locais e ignorados pelo Git. O catálogo versionado contém referências de terceiros com estado de evidência; ingestão não promove fonte a instrução. A memória é registro consultável, não treino de pesos. Skills são carregadas por tarefa, preservando o contexto adulto separado.

As integrações externas ficam em knowledge/integrations.json com estado explícito. Alterar registro não instala ferramenta. Mudar código de transporte, validação, escopo ou persistência exige rodar os testes correspondentes antes de empacotar.

A separação de módulos e os contratos de continuidade estão em CASSANDRA-REVERSE-EA.md. O servidor preserva a API pública anterior; serviços não dependem da interface.
