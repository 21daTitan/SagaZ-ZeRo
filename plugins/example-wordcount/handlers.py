"""Plugin de exemplo: função pura, sem acesso a arquivo/rede.

Modelo de um handler de ferramenta do SagaZ-ZeRo. Recebe apenas os argumentos
declarados no manifesto e devolve um dicionário serializável em JSON.
"""


def contar(texto: str = "") -> dict:
    palavras = [p for p in str(texto).split() if p]
    return {"palavras": len(palavras), "caracteres": len(str(texto)),
            "linhas": str(texto).count("\n") + 1 if texto else 0}
