from typing import Union, List, Dict, Any
from pydantic import Field, BaseModel


class BaseModel(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)


class VerificationMethod(BaseModel):
    id: str = Field()
    type: str = Field("Multikey")
    controller: str = Field()
    publicKeyMultibase: str = Field()


class Service(BaseModel):
    id: str = Field()
    type: str = Field()
    serviceEndpoint: str = Field()


class DidDocument(BaseModel):
    context: List[str] = Field(
        ["https://www.w3.org/ns/did/v1", "https://w3id.org/security/multikey/v1"]
    )
    id: str = Field()
    alsoKnownAs: List[str] = Field(None)
    authentication: List[str] = Field(None)
    assertionMethod: List[str] = Field(None)
    verificationMethod: List[VerificationMethod] = Field(None)
    service: List[Service] = Field(None)
