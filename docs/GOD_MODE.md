# Perfis de operação

O Core agora resolve o perfil `devocional` por padrão e aceita `deus` como perfil de sessão. O perfil Deus aumenta contexto e iterações, mas não remove a confirmação de ações destrutivas.

Uso no terminal:

```bash
python3 -m sagaz god
python3 -m sagaz god deus
```

Uso na Matrix:

```text
/god
```

Na Web UI, o botão `☩ PERFIL` altera o perfil apenas na memória do processo. Reiniciar o serviço volta ao valor de `SAGAZ_GOD_MODE` ou ao padrão devocional.

O modo não concede acesso remoto, não publica portas e não transforma o MCP em executor de shell. O shell continua sendo uma operação explícita por SSH.
