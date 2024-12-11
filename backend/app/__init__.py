import logging
from fastapi import FastAPI, APIRouter, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.routers import credentials, presentations
from config import settings
from app.plugins import AskarStorage

app = FastAPI(title=settings.PROJECT_TITLE, version=settings.PROJECT_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@api_router.get("/server/status", include_in_schema=False)
async def server_status():
    return JSONResponse(status_code=200, content={"status": "ok"})


@api_router.get("/.well-known/did.json", include_in_schema=False)
async def get_did_document():
    did_doc = await AskarStorage().fetch("didDocument", f"did:web:{settings.DOMAIN}")
    return JSONResponse(status_code=200, content=did_doc)


api_router.include_router(credentials.router)
api_router.include_router(presentations.router)


app.include_router(api_router)
