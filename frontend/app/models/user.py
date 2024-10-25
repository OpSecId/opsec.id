from typing import Dict, Any, Union, List
from pydantic import BaseModel, Field
import uuid

class BaseModel(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)
def _str_uuid():
    return str(uuid.uuid4())

class User(BaseModel):
    uid: str = Field()
    name: str = Field(None)
    email: str = Field(None)
    username: str = Field(None)

class WebAuthnCredential(BaseModel):
    uid: str = Field()
    credential_id: bytes = Field()
    credential_public_key: bytes = Field()
    current_sign_count: int = Field(None)