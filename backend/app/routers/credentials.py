from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from vcdm.models import Credential
from fastapi import HTTPException
from app.models.web_schemas import (
    UpdateCredentialRequest,
)
from app.plugins import DataIntegrity, VcJose, AskarStorage, BitstringStatusList
from datetime import datetime, timezone, timedelta
import json
import copy
import uuid
from app.utils import check_validity_period, process_request
from vcdm.models import Credential
# from vcdm.linked_data import LDProcessor
from app.linked_data import LDProcessor, LDProcessorError


router = APIRouter(tags=["Credentials"])


@router.post("/credentials/issue")
async def issue_credential(request: Request):
    request_body = await process_request(request)
    credential = request_body.get("credential")
    try:
        Credential.model_validate(credential)
    except:
        raise HTTPException(status_code=400)
    
    try:
        if LDProcessor().detect_undefined_terms(copy.deepcopy(credential)):
            raise HTTPException(status_code=400)
    except LDProcessorError:
        raise HTTPException(status_code=400)
    

    options = request_body.get("options")
    options = options if options else DataIntegrity().default_options()
    
    credential_id = str(uuid.uuid4())
    credential['id'] = f'urn:uuid:{credential_id}'

    if options.get('statusPurpose', None):
        status = BitstringStatusList()
        credential['credentialStatus'] = await status.create_entry(options.pop('statusPurpose'))

    if options.get('securingMechanism', None) == 'EnvelopingProof':
        vc_jwt = await VcJose().issue_credential(credential)
        enveloped_vc = {
            '@context': 'https://www.w3.org/ns/credentials/v2',
            'type': 'EnvelopedVerifiableCredential',
            'id': f'data:application/vc+jwt,{vc_jwt}'
        }
        return JSONResponse(status_code=201, content={"verifiableCredential": enveloped_vc})
        

    vc = await DataIntegrity().issue_credential(credential, options)

    # await AskarStorage().store('application/vc', credential_id, vc)
    # await AskarStorage().store('application/vc+jwt', credential_id, vc_jwt)
    return JSONResponse(status_code=201, content={"verifiableCredential": vc})


@router.get("/credentials/{credential_id}")
async def get_credential(credential_id: str, request: Request):
    if "application/vc+jwt" in request.headers["accept"]:
        return JSONResponse(
            status_code=200,
            headers={"Content-Type": "application/vc+jwt"},
            content=await AskarStorage().fetch("application/vc+jwt", credential_id)
        )
    return JSONResponse(
        status_code=200,
        headers={"Content-Type": "application/vc"},
        content=await AskarStorage().fetch("application/vc", credential_id)
    )


@router.post("/credentials/verify")
async def verify_issued_credential(request: Request):
    request_body = await process_request(request)
    vc = request_body.get("verifiableCredential")
    
    try:
        if LDProcessor().detect_undefined_terms(copy.deepcopy(vc)):
            raise HTTPException(status_code=400)
    except LDProcessorError:
        raise HTTPException(status_code=400)

    options = request_body.get("options")
    options = options if options else {}
    
    if vc.get('type', None) == 'EnvelopedVerifiableCredential':
        try:
            assert vc.get('@context') == 'https://www.w3.org/ns/credentials/v2'
            assert vc.get('id').startswith('data:')
            verification_results = {'verified': True}
        except:
            verification_results = {'verified': False}
    else:
        try:
            Credential.model_validate(vc)
        except:
            raise HTTPException(status_code=400)

        check_validity_period(vc)
        verification_results = await DataIntegrity().verify_credential(vc, options)
    
    return JSONResponse(
        status_code=200 if verification_results["verified"] else 400, 
        content=verification_results
    )


@router.post("/credentials/status")
async def update_issued_credential_status(request_body: UpdateCredentialRequest):
    return JSONResponse(status_code=200, content={})


@router.get("/credentials/status/{status_list_id}")
async def get_status_list_credential(status_list_id: str, request: Request):
    status_list_credential = await AskarStorage().fetch(
        "statusListCredential", status_list_id
    )
    
    if "application/vc+jwt" in request.headers["accept"]:
        status_list_vc = await VcJose().issue_credential(status_list_credential)
        return JSONResponse(
            status_code=200,
            headers={"Content-Type": "application/vc+jwt"},
            content=status_list_vc
        )
        
    options = DataIntegrity().default_options()
    options["created"] = datetime.now(timezone.utc).isoformat("T", "seconds")
    options["expires"] = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(
        "T", "seconds"
    )
    options = DataIntegrity().default_options()
    status_list_vc = await DataIntegrity().issue_credential(
        status_list_credential, options
    )
    return JSONResponse(
        status_code=200,
        headers={"Content-Type": "application/vc"},
        content=status_list_vc
    )
