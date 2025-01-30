from fastapi import APIRouter
from fastapi.responses import JSONResponse, RedirectResponse
from app.models.cid_document import CidDocument
from app.models.did_document import DidDocument, VerificationMethod
from config import settings

settings.MULTIKEY

router = APIRouter(tags=["Identifiers"])

@router.get("/", include_in_schema=False)
async def redirect_to_cid():
    return RedirectResponse(url="/.well-known/cid.json", status_code=302)

@router.get("/.well-known/cid.json", include_in_schema=False)
async def get_cid_document():
    cid_doc = CidDocument(
        id=f'https://{settings.DOMAIN}'
    ).model_dump()
    return JSONResponse(status_code=200, content=cid_doc)

@router.get("/.well-known/did.json", include_in_schema=False)
async def get_did_document():
    controller = f'did:web:{settings.DOMAIN}'
    did_doc = DidDocument(
        id=controller,
        verificationMethod=[
            VerificationMethod(
                id=f'{controller}#key-0',
                controller=controller,
                publicKeyMultibase=settings.MULTIKEY
            )
        ]
    ).model_dump()
    return JSONResponse(status_code=200, content=did_doc)