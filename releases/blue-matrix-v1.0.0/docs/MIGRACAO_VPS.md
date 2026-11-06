# Migração sem perda de dados — Hostinger KVM2

1. **Confirmar inventário:** versão, usuário, portas, supervisores (systemd/pm2/docker), unidades de serviço, bancos, arquivos de configuração e dependências do Core ativo.
2. **Backup separado:** exportar dados e segredos fora do repositório; validar restauração e hashes.
3. **Branch isolada:** publicar `feature/hooleesh33t-blue-matrix-v1` sem sobrescrever o diretório de produção.
4. **Prévia na VPS:** clonar projeto em `/opt/sagaz-blue-matrix-preview`, iniciar servidor em `127.0.0.1:8765` sem abrir o firewall.
5. **Teste local via SSH tunnel:** no Termux, `ssh -N -L 8765:127.0.0.1:8765 root@IP_CONFIRMADO` e acessar `http://127.0.0.1:8765` no navegador Android (encerrar eventual servidor local na mesma porta).
6. **Integração real:** mapear rotas e contratos do Core existente; implementar adaptador autenticado sem tocar na instalação original; testar tráfego real de IA, histórico e permissões.
7. **Cutover:** configurar `sagaz.21apvs.tech` por Nginx/TLS somente após login e proteção de API, validação de segurança e rollback.
8. **Desinstalação antiga:** só com evidência de paridade, backup recuperável e aprovação específica. Nunca apagar via script genérico.

`bash scripts/publicar_github.sh` apenas prepara e tenta enviar a branch mediante autenticação local. `bash scripts/preview_vps.sh` clona e inicializa **somente a prévia**, não modifica Core, DNS, Nginx ou unidades existentes.
