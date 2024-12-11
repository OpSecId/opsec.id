from typing import Dict, Any, List, Union
from pydantic import BaseModel, Field, field_validator
from app.plugins.linked_data import LinkedData
from app.models.proof import DataIntegrityProof
from vcdm.models import Credential


class BaseModel(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)


class Presentation(BaseModel):
    context: List[Union[str, dict]] = Field(alias="@context")
    type: List[str] = Field()
    id: str = Field(None)
    verifiableCredential: List[Credential] = Field(None)

    @field_validator("context")
    @classmethod
    def validate_presentation_context(cls, value):
        assert value[0] == "https://www.w3.org/ns/credentials/v2"
        assert LinkedData().is_valid_context(value.copy())
        for item in value[1:]:
            assert LinkedData().is_valid_context(item)
        return value

    @field_validator("id")
    @classmethod
    def validate_presentation_id(cls, value):
        if value.startswith("data:application/vp-ld"):
            vp_type = cls.type if isinstance(cls.type, list) else [cls.type]
            assert "EnvelopedVerifiablePresentation" in vp_type
        return value

    @field_validator("type")
    @classmethod
    def validate_presentation_type(cls, value):
        asserted_value = value if isinstance(value, list) else [value]
        assert (
            "VerifiablePresentation" in asserted_value
            or "EnvelopedVerifiablePresentation" in asserted_value
        )
        return value


class VerifiablePresentation(Presentation):
    proof: Union[DataIntegrityProof, List[DataIntegrityProof]] = Field(None)
