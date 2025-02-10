from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from app.plugins import DataIntegrity, VcJose
from vcdm.models import Presentation
import copy
from app.utils import process_request
from app.linked_data import LDProcessor, LDProcessorError

router = APIRouter(tags=["Presentations"])


@router.post("/presentations")
async def create_signed_presentation(request: Request):
    request_body = await process_request(request)
    presentation = request_body.get("presentation")
    
    try:
        Presentation.model_validate(presentation)
    except:
        raise HTTPException(status_code=400)
    
    try:
        if LDProcessor().detect_undefined_terms(copy.deepcopy(presentation)):
            raise HTTPException(status_code=400)
    except LDProcessorError:
        raise HTTPException(status_code=400)

    options = request_body.get("options")
    options = options if options else DataIntegrity().default_options()

    vp = await DataIntegrity().add_proof(presentation, options)
    vp_jwt = await VcJose().sign_presentation(vp)

    if options.get('securingMechanism', None) == 'EnvelopingProof':
        enveloped_vp = {
            '@context': 'https://www.w3.org/ns/credentials/v2',
            'type': 'EnvelopedVerifiablePresentation',
            'id': f'data:application/vp+jwt,{vp_jwt}'
        }
        return JSONResponse(status_code=201, content={"verifiablePresentation": enveloped_vp})
    
    return JSONResponse(status_code=201, content={"verifiablePresentation": vp})


@router.post("/presentations/verify")
async def verify_signed_presentation(request: Request):
    request_body = await process_request(request)
    vp = request_body.get("verifiablePresentation")
    
    try:
        LDProcessor().detect_undefined_terms(copy.deepcopy(vp))
    except LDProcessorError:
        raise HTTPException(status_code=400)

    options = request_body.get("options")
    options = options if options else {}
    
    if vp.get('type', None) == 'EnvelopedVerifiablePresentation':
        try:
            assert vp.get('@context') == 'https://www.w3.org/ns/credentials/v2'
            assert vp.get('id').startswith('data:')
            verification_results = {'verified': True}
        except:
            verification_results = {'verified': False}
    else:
        try:
            Presentation.model_validate(vp)
        except:
            raise HTTPException(status_code=400)

        verification_results = await DataIntegrity().verify_credential(vp, options)
        verification_results = {'verified': True}
    
    
    return JSONResponse(
        status_code=200 if verification_results["verified"] else 400, 
        content=verification_results
    )
