from config import settings
from typing import Dict, Any
from pydantic import BaseModel, Field
from vcdm.models import Credential
from app.models import IssuanceOptions, VerificationOptions, Presentation, VerifiablePresentation
import re, uuid
from datetime import datetime
from app.utils import id_from_string


class RequestBody(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)


class IssueCredentialRequest(RequestBody):
    credential: Credential = Field()
    options: IssuanceOptions = Field(None)
    
class VerifyCredentialRequest(RequestBody):
    verifiableCredential: Credential = Field()
    options: VerificationOptions = Field(None)
    
class UpdateCredentialRequest(RequestBody):
    credentialId: str = Field(example=id_from_string('credentialIdExample'))
    credentialStatus: dict = Field()

class CreatePresentationRequest(RequestBody):
    presentation: Presentation = Field()
    options: IssuanceOptions = Field(None)

class VerifyPresentationRequest(RequestBody):
    verifiablePresentation: VerifiablePresentation = Field()
    options: IssuanceOptions = Field(None)


