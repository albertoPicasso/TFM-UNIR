from typing import Dict, List
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class GetAnswerInputPayload(BaseModel):
    messages: List[Message]
