from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    upload_date: datetime
    num_pages: int
    
    class Config:
        from_attributes = True
