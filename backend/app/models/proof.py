from typing import Dict, Any, List, Union
from pydantic import BaseModel, Field
from config import settings
from pydantic.json_schema import SkipJsonSchema


class BaseModel(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)


class DataIntegrityProof(BaseModel):
    id: SkipJsonSchema[str] = Field(None)
    type: Union[str, List[str]] = Field(example="DataIntegrityProof")
    cryptosuite: str = Field(example="eddsa-jcs-2022")
    verificationMethod: str = Field(
        example=f"did:key:{settings.MULTIKEY}#{settings.MULTIKEY}"
    )
    created: SkipJsonSchema[str] = Field(None)
    expires: SkipJsonSchema[str] = Field(None)
    proofPurpose: str = Field(example="assertionMethod")
    proofValue: str = Field(
        example="z5FoDF2xxXxnvKLd9ArsPUgCrQbvSGPCQStHa8vU3jntKZSRnW389jFhp6y2KcBUrKxoTNQzDQCKK2zmJG2ZoJD5e"
    )
