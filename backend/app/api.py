from fastapi import FastAPI, APIRouter, Request
# from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.models.validations import ValidationException
from app.routers import did, credentials
from config import settings
import os
import logging
import json

app = FastAPI(title=settings.PROJECT_TITLE, version=settings.PROJECT_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter()

api_router.include_router(did.router)
api_router.include_router(credentials.router, tags=["Credentials"], prefix='/credentials')


@api_router.get("/server/status", include_in_schema=False)
async def server_status():
    return JSONResponse(status_code=200, content={"status": "ok"})


app.include_router(api_router)


# logger = logging.getLogger('uvicorn.error')
# logger.setLevel(logging.INFO)

# @app.exception_handler(RequestValidationError)
# async def _(request: Request,
#             exc: RequestValidationError):
#     try:
#         # if type(await request.body()) == type(b''):
#         # logger.debug(json.dumps(await request.json()))
#         # logger.debug(exc)
#         # logger.debug(type(await request.json()))
#         # logger.debug(request)
#         logger.info(request.headers)
#         logger.info(exc)
#         # logger.info(await request.body())
#         #     logger.info((await request.body()).decode(encoding='utf-8'))
#         #     return await request.body()
#         #     return json.loads((await request.body()).decode(encoding='utf-8'))
#     except json.decoder.JSONDecodeError:
#         # Request had invalid or no body
#         pass

#     raise exc
