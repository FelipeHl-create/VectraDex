from fastapi import FastAPI, Request
import logging, json, sys
from logging.handlers import RotatingFileHandler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .core.config import settings
from .api.api_v1 import api_router
from .db.session import engine
from .db.base import Base

# Criar tabelas no startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="VectraDex API", version="1.0.0")

# Logging configurável (JSON opcional)
class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%SZ"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

def _setup_logging():
    root = logging.getLogger()
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root.setLevel(level)
    # limpar handlers existentes (evita duplicado em reload)
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler(sys.stdout)
    if settings.LOG_JSON:
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
    root.addHandler(handler)
    # arquivo rotativo opcional
    if settings.LOG_FILE:
        file_handler = RotatingFileHandler(settings.LOG_FILE, maxBytes=settings.LOG_MAX_BYTES, backupCount=settings.LOG_BACKUP_COUNT)
        if settings.LOG_JSON:
            file_handler.setFormatter(_JsonFormatter())
        else:
            file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
        root.addHandler(file_handler)

_setup_logging()

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")] if settings.CORS_ORIGINS else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Headers de segurança básicos
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Redireciona HTTP->HTTPS quando ativado em produção
        if settings.FORCE_HTTPS and request.url.scheme == "http":
            https_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(https_url), status_code=307)
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        # CSP básica; ajuste conforme for servir assets externos
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'" ,
        )
        if settings.HSTS_ENABLED:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
login_fail_counter = Counter("vd_login_failures_total", "Falhas de login", ["reason"])  # invalid_credentials|rate_limited

# Static e Templates (UI simples)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
_templates_env = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape(["html", "xml"])  # noqa: WPS317
)

@app.get("/", response_class=HTMLResponse)
async def index(_: Request) -> HTMLResponse:
    template = _templates_env.get_template("index.html")
    return HTMLResponse(template.render())

@app.get("/login", response_class=HTMLResponse)
async def login_page(_: Request) -> HTMLResponse:
    template = _templates_env.get_template("login.html")
    return HTMLResponse(template.render())

@app.get("/produtos", response_class=HTMLResponse)
async def products_page(_: Request) -> HTMLResponse:
    template = _templates_env.get_template("products.html")
    return HTMLResponse(template.render())

@app.get("/maquinas", response_class=HTMLResponse)
async def machines_page(_: Request) -> HTMLResponse:
    template = _templates_env.get_template("machines.html")
    return HTMLResponse(template.render())

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(_: Request) -> HTMLResponse:
    template = _templates_env.get_template("dashboard.html")
    return HTMLResponse(template.render())

# API
app.include_router(api_router, prefix="/api")
