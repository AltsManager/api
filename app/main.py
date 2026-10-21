from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.admin import mount_admin
from app.core.config import get_settings
from app.core.exceptions import NotFoundError, ValidationError
from app.routers import auth, counterparties, documents, entities, health, investments, transactions

app = FastAPI(title="AltsManager API")


class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    """Rejects requests whose declared Content-Length exceeds the configured limit.

    This is a cheap, early rejection based on the client-supplied header -- it
    doesn't protect against a chunked-encoding client lying about size, which
    the upload-size check in app.services.documents backstops once the body has
    been read.
    """

    async def dispatch(self, request: Request, call_next):
        max_size = get_settings().max_upload_size_bytes
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                too_large = int(content_length) > max_size
            except ValueError:
                too_large = False
            if too_large:
                return JSONResponse(status_code=413, content={"detail": "Request body too large"})
        return await call_next(request)


app.add_middleware(MaxBodySizeMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
