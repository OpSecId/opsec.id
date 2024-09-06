from typing import Union, List, Dict
from pydantic import Field, AliasChoices, field_validator
from app.models.base import BaseModel
from datetime import datetime
import app.utilities.validations as _v
    

class NameField(BaseModel):
    pass
    
class DescriptionField(BaseModel):
    pass

class GenericModel(BaseModel):
    type: Union[str, List[str]]
    id: str = Field()
    name: Union[str, NameField] = Field()
    description: Union[str, DescriptionField] = Field()

class Issuer(GenericModel):
    pass

class CredentialSubject(GenericModel):
    pass

class CredentialSchema(GenericModel):
    pass

class CredentialStatus(GenericModel):
    pass

class TermsOfUse(GenericModel):
    pass

class RenderMethod(GenericModel):
    pass

class Credential(GenericModel):
    context: List[str] = Field(alias="@context")
    type: List[str] = Field()
    id: str = Field(None)
    issuer: Union[Dict[str, str], str] = Field()
    name: str = Field(None)
    description: str = Field(None)
    validFrom: str = Field(None)
    validUntil: str = Field(None)
    credentialSubject: Union[List[dict], dict] = Field()
    credentialStatus: Union[List[dict], dict] = Field(None)
    credentialSchema: Union[List[dict], dict] = Field(None)
    termsOfUse: Union[List[dict], dict] = Field(None)
    refreshService: Union[List[dict], dict] = Field(None)
    evidence: Union[List[dict], dict] = Field(None)
    renderMethod: Union[List[dict], dict] = Field(None)

    @field_validator("context")
    @classmethod
    def validate_context(cls, value):
        assert isinstance(value, list)
        assert value[0] == ''
        for item in value[1:]:
            assert _v.valid_context_item(item)
        return value

    @field_validator("type")
    @classmethod
    def validate_credential_type(cls, value):
        _v.valid_type(value)
        assert isinstance(value, str) or isinstance(value, list)
        assert value == 'VerifiableCredential' if isinstance(value, str) else 'VerifiableCredential' in value, 'MUST contain VerifiableCredential'
        return value

    @field_validator("id")
    @classmethod
    def validate_credential_id(cls, value):
        assert isinstance(value, str)
        return value

    @field_validator("issuer")
    @classmethod
    def validate_issuer(cls, value):
        assert isinstance(value, str) or isinstance(value, dict)
        assert 'id' in value if isinstance(value, dict) else True
        assert value if isinstance(value, str) else value['id']
        return value

    @field_validator("validFrom")
    @classmethod
    def validate_valid_from_date(cls, value):
        assert _v.valid_xml_datetimestamp(value)
        return value

    @field_validator("validUntil")
    @classmethod
    def validate_valid_until_date(cls, value):
        assert _v.valid_xml_datetimestamp(value)
        return value

    @field_validator("credentialSubject")
    @classmethod
    def validate_credential_subject(cls, value):
        assert isinstance(value, dict) or isinstance(value, list)
        assert all(isinstance(item, dict) for item in value) if isinstance(value, list) else True
        return value

    @field_validator("credentialStatus")
    @classmethod
    def validate_credential_status(cls, value):
        assert isinstance(value, dict) or isinstance(value, list)
        assert all(isinstance(item, dict) for item in value) if isinstance(value, list) else True
        assert 'type' in value or all('type' in item for item in value)
        return value
    
    def add_validity_period():
        validFrom = str(datetime.now().isoformat("T", "seconds"))
        validUntil = str(datetime.now().isoformat("T", "seconds"))