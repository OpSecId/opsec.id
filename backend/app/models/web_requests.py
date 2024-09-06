from config import settings
from typing import Union, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
import re, uuid
from datetime import datetime
from app.utilities.examples import EXAMPLE_CREDENTIAL

class RequestBody(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)

class IssueCredential(RequestBody):
    credential: dict = Field(example=EXAMPLE_CREDENTIAL)
    options: dict = Field(example={})