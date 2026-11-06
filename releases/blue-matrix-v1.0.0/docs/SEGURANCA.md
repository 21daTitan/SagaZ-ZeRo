# Segurança, proteção do código e resiliência

- **Engenharia reversa:** código JavaScript entregue ao navegador pode ser inspecionado. Não há como impedir completamente a análise. Mantenha prompts proprietários, chaves, lógica sensível e execução privilegiada no servidor.
- **Chaves:** nunca em Git, HTML, localStorage, console, logs ou payloads de front. No MVP, uma chave **do operador** é mantida apenas em variável de ambiente. BYOK por usuário requer vault isolado, ACL e rotação; ainda não está implementado.
- **Autenticação:** sessão cookie HttpOnly/SameSite=Strict e cabeçalho próprio de requisições. Exigir HTTPS no proxy e `SAGAZ_COOKIE_SECURE=1` em produção. Credenciais administrativas longas e únicas.
- **Acesso externo:** o serviço usa 127.0.0.1; publicar só por reverse proxy TLS com rate limiting, autenticação adicional e monitoramento. Não abrir a porta 8765 na internet.
- **Comandos e agentes:** executor não implementado no frontend; futura execução deve ocorrer em ambiente restrito, com autorização de escopo, timeout, logs e confirmação para alterações críticas.
- **Arquivos:** apenas prévia de textos pequenos no navegador. Na futura API, aplicar limite de tamanho, detecção MIME, sandbox, proteção contra ZIP bombs e varredura; proibir acesso a paths arbitrários.
- **Atualizações:** backups imutáveis, checksums, CI de testes, dependências fixadas, rollback, migração controlada. Nenhuma proteção garante funcionamento eterno.
- **Uso compartilhado:** consentimento claro para qualquer telemetria; não captar tokens ou executar mineração sem autorização explícita, visível e revogável.
- **Política de origem:** verificar domínio, CSP, segurança de cabeçalhos e revogação/rotação de sessões antes de produção multiusuário.

**Alcance:** a implementação incluída é protótipo local/single-admin com controles básicos, não uma auditoria certificada de segurança.
