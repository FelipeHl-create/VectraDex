from fastapi import APIRouter
from .routes import auth, products, machines, dashboard, labels, export

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(machines.router, prefix="/machines", tags=["machines"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(labels.router, prefix="/labels", tags=["labels"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
