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


class CidDocument(BaseModel):
    context: List[str] = Field(
        ["https://www.w3.org/ns/cid/v1"]
    )
    id: str = Field()
    alsoKnownAs: List[str] = Field(None)
    authentication: List[str] = Field()
    assertionMethod: List[str] = Field()
    verificationMethod: List[VerificationMethod] = Field()
    service: List[Service] = Field(None)
