from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.models.web_schemas import IssueCredentialRequest, VerifyCredentialRequest, UpdateCredentialRequest
from app.plugins import DataIntegrity, VcJose, AskarStorage
from datetime import datetime, timezone, timedelta
import json
from app.utils import check_validity_period

router = APIRouter(tags=["Credentials"])


@router.post("/credentials/issue")
async def issue_credential(request_body: IssueCredentialRequest):
    credential = request_body.credential.model_dump()
    options = request_body.options.model_dump()
    if "securingMechanism" in options and options['securingMechanism'] == "EnvelopingProof":
        vc = await VcJose().issue_credential(credential)
    else:
        options = DataIntegrity().default_options()
        vc = await DataIntegrity().issue_credential(credential, options)
    return JSONResponse(status_code=201, content={"verifiableCredential": vc})


@router.post("/credentials/verify")
async def verify_issued_credential(request_body: VerifyCredentialRequest):
    vc = request_body.verifiableCredential.model_dump()
    options = request_body.options.model_dump()
    
    check_validity_period(vc)
    
    if "securingMechanism" in options and options['securingMechanism'] == "EnvelopingProof":
        vc = await VcJose().verify_credential(vc)
    else:
        verification_results = await DataIntegrity().verify_credential(vc, options)
    if verification_results['verified']:
        return JSONResponse(status_code=200, content=verification_results)
    return JSONResponse(status_code=400, content=verification_results)


@router.post("/credentials/status")
async def update_issued_credential_status(request_body: UpdateCredentialRequest):
    credential = request_body.credential.model_dump()
    options = request_body.options.model_dump()
    if "securingMechanism" in options and options['securingMechanism'] == "EnvelopingProof":
        vc = await VcJose().issue_credential(credential)
    else:
        vc = await DataIntegrity().issue_credential(credential, options)
    return JSONResponse(status_code=200, content={"verifiableCredential": vc})


@router.get("/credentials/status/{status_list_id}")
async def get_status_list_credential(status_list_id: str):
    status_list_credential = await AskarStorage().fetch('statusListCredential', status_list_id)
    status_list_credential['validFrom'] = datetime.now(timezone.utc).isoformat('T', 'seconds')
    status_list_credential['validUntil'] = (datetime.now(timezone.utc)+ timedelta(minutes=5)).isoformat('T', 'seconds')
    options = DataIntegrity().default_options()
    status_list_vc = await DataIntegrity().issue_credential(status_list_credential, options)
    return JSONResponse(status_code=200, content=status_list_vc)
