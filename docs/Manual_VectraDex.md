# Manual do VectraDex (Uso e Implantação)

## 1. Visão geral
- VectraDex é um sistema de gestão de produção e estoque (FastAPI + SQLite) com interface web simples (Jinja2) e API documentada em `/docs`.
- Público‑alvo: operações industriais com controle de produtos, impressão de etiquetas, registro de paradas de máquinas e acompanhamento de métricas.

## 2. Perfis e permissões
- Admin/gerente: acesso completo (dashboard com KPIs/valores, cadastros, exportações).
- Operador: acesso a máquinas e produção (sem valores monetários; sem KPIs do dashboard).
- Usuários de demonstração (criados pelo seed; altere as senhas após testes):
  - admin@empresa.com.br / Admin123!
  - usuario.id@empresa.com.br / User123!

## 3. Requisitos
- Python 3.11
- Sistema operacional: Windows (testado), Linux ou macOS
- Porta livre (padrão 8000)

## 4. Instalação local (dev)
1) Abrir terminal na pasta `vectradex/` e criar venv:
```
python -m venv .venv
. ./.venv/Scripts/Activate.ps1   # Windows PowerShell
# ou: source ./.venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```
2) Executar API/UI:
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
3) Acessar: `http://localhost:8000`

## 5. Configuração por ambiente (sem expor segredos)
- Definir variáveis de ambiente no sistema/servidor (não commitar `.env`).
- Variáveis esperadas (apenas nomes, sem valores): `SECRET_KEY`, `PASSWORD_RESET_SECRET`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALGORITHM`, `DATABASE_URL`, `CORS_ORIGINS`, `COOKIE_SECURE`, `HSTS_ENABLED`, `FORCE_HTTPS`, `LOG_JSON`, `LOG_LEVEL`, `LOG_FILE`, `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT`, `WEBHOOK_URL`, `LOGIN_MAX_ATTEMPTS`, `LOGIN_WINDOW_SECONDS`, `LOGIN_LOCKOUT_SECONDS`.

## 6. Primeiros passos (uso do sistema)
1) Login em `/login`.
2) Navegação (menu lateral):
   - Dashboard (admin/gerente): visão com KPIs, série histórica e motivos de parada.
   - Produtos: busca, cadastro, atualização e impressão de etiqueta (PNG). Exportações: CSV/XLSX.
   - Máquinas: status, registro de paradas e histórico.
   - API Docs: documentação interativa dos endpoints.
3) Exportações: seção específica na página inicial (`/`) com links para CSV/XLSX.

## 7. Segurança (resumo operacional)
- Autenticação com token em cookie HttpOnly; rate limiting no login por IP/usuário.
- CORS restrito por configuração; cabeçalhos de segurança e CSP; HTTPS/HSTS configuráveis.
- Segredos exclusivamente via ambiente/secret store; nunca em repositório ou UI.
- Logs estruturados (JSON) e webhook opcional para alertas de falha de login.

## 8. Observabilidade básica
- Endpoint `/metrics` (Prometheus) com contadores/latências por rota.
- Métricas customizadas: falhas de login e tempo de geração de séries do dashboard.
- Integração sugerida: Prometheus + Grafana (coleção do endpoint `/metrics`).

## 9. Implantação em empresa (produção)
### 9.1. Padrões mínimos
- Definir variáveis de ambiente (secrets) no servidor/CI.
- Habilitar HTTPS e cookies seguros: `FORCE_HTTPS=True`, `HSTS_ENABLED=True`, `COOKIE_SECURE=True`.
- Restringir `CORS_ORIGINS` aos domínios oficiais.

### 9.2. Servidor Linux (systemd) – exemplo
1) Criar venv, instalar dependências e testar com `uvicorn`.
2) Service unit (exemplo `/etc/systemd/system/vectradex.service`):
```
[Unit]
Description=VectraDex API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/vectradex
Environment="PYTHONPATH=/opt/vectradex"
EnvironmentFile=/opt/vectradex/.env   # arquivo local seguro (permissões restritas) ou export no profile
ExecStart=/opt/vectradex/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
3) `systemctl daemon-reload && systemctl enable --now vectradex`.
4) Reverse proxy (Nginx) com TLS/Let's Encrypt apontando para `127.0.0.1:8000`.

### 9.3. Servidor Windows (serviço)
- Executar em venv e usar um gerenciador de serviço (ex.: NSSM) para manter o processo `uvicorn` ativo.
- TLS via proxy (IIS/Nginx/Traefik) com binding ao 8000.

### 9.4. Banco de dados
- Padrão: SQLite local (arquivo `vectradex.db`). Para multiusuário/alta disponibilidade, migrar para Postgres e ajustar `DATABASE_URL`.
- Backup: cópia fria do arquivo SQLite com o serviço parado; em Postgres, usar `pg_dump`.

## 10. Backup e recuperação
- Agendar backup diário do banco e dos diretórios `data/` e `logs/` (se configurado).
- Testar recuperação periodicamente em ambiente isolado.

## 11. Troubleshooting
- 401/403: verificar autenticação e perfil do usuário.
- 429 no login: aguardar período de lockout; revisar tentativas e origem de IP.
- CORS: confirmar `CORS_ORIGINS`.
- HTTPS/cookies não persistem: validar `COOKIE_SECURE`, `FORCE_HTTPS`, proxy TLS e `SameSite`.
- Métricas vazias: acessar `/metrics`; verificar firewall/proxy.

## 12. Boas práticas contínuas
- Atualizar dependências periodicamente.
- Usar hooks `pre-commit` (lint + detect-secrets) e CI do repositório.
- Revisar logs/alertas de segurança e de disponibilidade.

---

Este manual não expõe segredos. Em caso de dúvidas de segurança, trate variáveis e chaves exclusivamente via mecanismos de segredo do seu ambiente (não compartilhe por e‑mail, chat ou repositório público).
