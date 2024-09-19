from typing import Dict, Any, Union, List
from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

class BaseModel(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)


class IssuanceOptions(BaseModel):
    type: str = Field(None, example='DataIntegrityProof')
    cryptosuite: str = Field(None, example='eddsa-jcs-2022')
    previousProof: SkipJsonSchema[Union[str, List[str]]] = Field(None)
    securingMechanism: SkipJsonSchema[str] = Field(None)
    statusPurpose: Union[str, List[str]] = Field(None, example='revocation')
    credentialId: SkipJsonSchema[str] = Field(None)


class VerificationOptions(BaseModel):
    returnResults: bool = Field(None, example=True)
    returnCredential: bool = Field(None, example=True)
    returnProblemDetails: bool = Field(None, example=True)
