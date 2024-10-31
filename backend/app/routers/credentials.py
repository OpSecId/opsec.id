from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from vcdm.models import Credential
from fastapi import HTTPException
from app.models.web_schemas import IssueCredentialRequest, VerifyCredentialRequest, UpdateCredentialRequest
from app.plugins import DataIntegrity, VcJose, AskarStorage, BitstringStatusList
from datetime import datetime, timezone, timedelta
import json
import uuid
from app.utils import check_validity_period
from vcdm.linked_data import LDProcessor

router = APIRouter(tags=["Credentials"])


@router.post("/credentials/issue")
async def issue_credential(request_body: IssueCredentialRequest, envelope: str | None = None):
    request_body = request_body.model_dump()
    credential = request_body.get('credential')
    options = DataIntegrity().default_options()
    
    # LDProcessor().is_valid_context(credential['@context'].copy())
    
    if request_body.get('options'):
        options = request_body.get('options')
    
    if 'id' not in credential:
        credential_id = f'urn:uuid:{str(uuid.uuid4())}'
        credential['id'] = credential_id
        
    if 'statusPurpose' in options:
        credential['credentialStatus'] = await BitstringStatusList().create_entry(options.pop('statusPurpose'))
    
    vc = await DataIntegrity().issue_credential(credential, options)
    
    await AskarStorage().store('credential', credential['id'], vc)
    
    if envelope == '':
        vc = await VcJose().issue_credential(vc)
        
    return JSONResponse(status_code=201, content={"verifiableCredential": vc})


@router.get("/credentials/{credential_id}")
async def get_credential(credential_id: str, response: Response, request: Request):
    vc = await AskarStorage().fetch('credential', credential_id)
    if request.headers['accept'] == 'application/vc-ld+jwt':
        vc = await VcJose().issue_credential(vc)
        vc_jwt = vc['id'].split(',')[-1]
        headers = {"Content-Type": "application/vc-ld+jwt"}
        return JSONResponse(status_code=200, content=vc_jwt, headers=headers)
    
    headers = {"Content-Type": "application/vc"}
    return JSONResponse(status_code=200, content=vc, headers=headers)


@router.post("/credentials/verify")
async def verify_issued_credential(request_body: VerifyCredentialRequest):
    
    request_body = request_body.model_dump()
    vc = request_body.get('verifiableCredential')
    options = {}
    
    # LDProcessor().is_valid_context(vc['@context'].copy())
    
    if request_body.get('options'):
        options = request_body.get('options')
    
    check_validity_period(vc)
    
    if "EnvelopedVerifiableCredential" in vc['type']:
        verification_results = await VcJose().verify_credential(vc)
    else:
        verification_results = await DataIntegrity().verify_credential(vc, options)
    if verification_results['verified']:
        return JSONResponse(status_code=200, content=verification_results)
    return JSONResponse(status_code=400, content=verification_results)


@router.post("/credentials/status")
async def update_issued_credential_status(request_body: UpdateCredentialRequest):
    return JSONResponse(status_code=200, content={})


@router.get("/credentials/status/{status_list_id}")
async def get_status_list_credential(status_list_id: str, envelope: str | None = None):
    status_list_credential = await AskarStorage().fetch('statusListCredential', status_list_id)
    options = DataIntegrity().default_options()
    options['created'] = datetime.now(timezone.utc).isoformat('T', 'seconds')
    options['expires'] = (datetime.now(timezone.utc)+ timedelta(minutes=5)).isoformat('T', 'seconds')
    status_list_vc = await DataIntegrity().issue_credential(status_list_credential, options)
    if envelope == '':
        status_list_vc = await VcJose().issue_credential(status_list_vc)
    return JSONResponse(status_code=200, content=status_list_vc)
