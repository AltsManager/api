from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.admin import mount_admin
from app.core.exceptions import NotFoundError, ValidationError
from app.routers import auth, counterparties, documents, entities, health, investments, transactions

app = FastAPI(title="AltsManager API")


@app.exception_handler(NotFoundError)
def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ValidationError)
def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(entities.router)
app.include_router(counterparties.router)
app.include_router(investments.router)
app.include_router(transactions.router)
app.include_router(documents.router)

mount_admin(app)
