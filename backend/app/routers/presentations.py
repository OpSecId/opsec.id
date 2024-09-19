from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.models.web_schemas import CreatePresentationRequest, VerifyPresentationRequest
from app.plugins import DataIntegrity, VcJose

router = APIRouter(tags=["Presentations"])


@router.post("/presentations")
async def create_signed_presentation(request_body: CreatePresentationRequest):
    presentation = request_body.presentation.model_dump()
    options = request_body.options.model_dump()
    if "securingMechanism" in options and options['securingMechanism'] == "EnvelopingProof":
        vp = await VcJose().create_presentation(presentation)
    else:
        vp = await DataIntegrity().create_presentation(presentation, options)
    return JSONResponse(status_code=201, content={"verifiablePresentation": vp})


@router.post("/presentations/verify")
async def verify_signed_presentation(request_body: VerifyPresentationRequest):
    vp = request_body.verifiablePresentation.model_dump()
    options = request_body.options.model_dump()
    verified={}
    return JSONResponse(status_code=200, content=verified)
