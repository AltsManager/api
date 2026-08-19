from fastapi import FastAPI

from app.routers import health

app = FastAPI(title="AltsManager API")

app.include_router(health.router)
