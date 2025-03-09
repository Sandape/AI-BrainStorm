from pydantic import BaseModel, Field, validator
from typing import List, Optional

class ChatRequest(BaseModel):
    model: str
    message: str


class DiscussRequest(BaseModel):
    topic: str
    models: List[str]

    @validator('models')
    def validate_models(cls, v):
        if not v:
            raise ValueError("At least one model must be selected")
        if len(v) > 3:
            raise ValueError("Maximum 3 models allowed")
        return v 