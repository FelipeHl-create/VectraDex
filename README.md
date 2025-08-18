# VectraDex

Sistema de gestão de produção e estoque com FastAPI + SQLite, interface server-rendered com Jinja2 e estilo moderno. Inclui cadastro e controle de produtos, monitoramento de máquinas, emissão de etiquetas e dashboards.

## Principais recursos
- Dashboard com KPIs, gráficos e motivos de parada
- Gestão de produtos (CRUD, busca, localização, etiqueta PNG)
- Visão de máquinas e registro de paradas
- Exportações em CSV e XLSX
- Documentação interativa da API em `/docs`

## Requisitos
- Python 3.11 (Windows testado; funciona em Linux/macOS)

## Instalação e execução (local)
```powershell
cd vectradex
python -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force  # se necessário
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: `http://localhost:8000`

Páginas da interface:
- `/` Dashboard resumido + exportações
- `/dashboard` Gráficos e KPIs
- `/produtos` Gestão de produtos e impressão de etiquetas
- `/maquinas` Status e paradas
- `/login` Autenticação

APIs: `http://localhost:8000/docs`

## Configuração por ambiente
Crie um arquivo `.env` na raiz do projeto (use como referência os campos abaixo) e NUNCA commit esse arquivo:
```
# Omitir para gerar segredo aleatório em runtime (recomendado em dev)
SECRET_KEY=
PASSWORD_RESET_SECRET=
ACCESS_TOKEN_EXPIRE_MINUTES=120
ALGORITHM=HS256
DATABASE_URL=sqlite:///./vectradex.db
# Produção: defina apenas domínios confiáveis (ex.: https://app.suaempresa.com)
CORS_ORIGINS=http://localhost:8000
```

## Estrutura do projeto
```
vectradex/
  app/
    api/                # Rotas de API (v1)
    core/               # Configurações e utilitários
    db/                 # Sessão e base declarativa SQLAlchemy
    models/             # Modelos e tabelas
    schemas/            # Pydantic Schemas
    templates/          # Páginas Jinja2 (UI)
    static/             # CSS/Imagens
    main.py             # App FastAPI e montagem da UI
  scripts/              # Utilidades (ex.: seed)
  requirements.txt
  README.md
```

## Exportações
- Produtos CSV: `/api/export/products/csv`
- Produtos XLSX: `/api/export/products/xlsx`
- Produção CSV: `/api/export/production/csv`
- Produção XLSX: `/api/export/production/xlsx`

## Segurança e boas práticas
- Nunca exponha segredos (chaves/API/credenciais) no repositório ou na UI.
- Use `.env` em desenvolvimento e Secrets do repositório/Actions em CI/CD.
- Restrinja `CORS_ORIGINS` a domínios específicos em produção.
- Não registre segredos nos logs.
- Rotacione chaves comprometidas imediatamente e limpe históricos (BFG/git-filter-repo) se necessário.

### Rate limiting
O endpoint de login possui limite de tentativas por IP e por usuário (janela/bloqueio configuráveis em `app/core/config.py` via env: `LOGIN_MAX_ATTEMPTS`, `LOGIN_WINDOW_SECONDS`, `LOGIN_LOCKOUT_SECONDS`).

### HTTPS e cookies
- Em produção, defina no `.env`:
  - `COOKIE_SECURE=True` (cookies enviados apenas via HTTPS)
  - `HSTS_ENABLED=True` (Strict-Transport-Security)
  - `FORCE_HTTPS=True` (redireciona HTTP→HTTPS)

### Pre-commit (opcional, recomendado)
Instale pre-commit e ative o conjunto de hooks configurado:
```bash
pip install pre-commit detect-secrets ruff
pre-commit install
```
Isso executará checagens de formatação, lint e varredura de segredos em cada commit.

### Log estruturado
Ative logs JSON definindo `LOG_JSON=True` no `.env`. Configure nível/arquivo rotativo:
```
LOG_JSON=True
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_MAX_BYTES=1048576
LOG_BACKUP_COUNT=5
```
Webhook opcional para alertas (ex.: Discord/Slack):
```
WEBHOOK_URL=https://seu-webhook
```

## Dicas e solução de problemas
- Execução de script bloqueada (Windows PowerShell):
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
  ```
- Porta ocupada: altere a porta no comando do servidor (`--port 8001`).
- Ambiente virtual: confirme que o prompt contém `(.venv)` antes de rodar `uvicorn`.

## Como contribuir
1. Crie um branch a partir de `main`
2. Faça commits pequenos e descritivos
3. Abra um Pull Request

---

Nota: O projeto é desenvolvido com práticas robustas e foco em segurança por padrão. Detalhes de implementação interna não são expostos neste documento.
