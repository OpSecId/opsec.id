from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.web_requests import IssueCredential
from app.plugins import AskarWallet

router = APIRouter()

@router.post("/issue")
async def issue_credential(request_body: IssueCredential):
    credential = request_body.credential.model_dump()
    options = request_body.options.model_dump(by_alias=True, exclude_none=True)
    vc = AskarWallet().issue_credential(credential, options)
    return JSONResponse(status_code=201, content={"verifiableCredential": vc})