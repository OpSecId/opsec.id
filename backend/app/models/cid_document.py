from typing import Union, List, Dict, Any
from pydantic import Field, BaseModel
from app.models.did_document import VerificationMethod, Service


class BaseModel(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)


class CidDocument(BaseModel):
    # context: List[str] = Field(
    #     ["https://www.w3.org/ns/cid/v1"]
    # )
    id: str = Field()
    alsoKnownAs: List[str] = Field(None)
    authentication: List[str] = Field(None)
    assertionMethod: List[str] = Field(None)
    verificationMethod: List[VerificationMethod] = Field(None)
    service: List[Service] = Field(None)
