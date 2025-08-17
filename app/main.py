from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .core.config import settings
from .api.api_v1 import api_router
from .db.session import engine
from .db.base import Base

# Criar tabelas no startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="VectraDex API", version="1.0.0")

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")] if settings.CORS_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
