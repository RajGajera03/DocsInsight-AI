from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MessageBase(BaseModel):
    role: str
    content: str

class MessageResponse(MessageBase):
    id: int
    session_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionCreate(BaseModel):
    document_id: Optional[int] = None

class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    document_id: Optional[int]
    created_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    session_id: int
    question: str
    document_id: Optional[int] = None
