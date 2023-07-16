from typing import Optional
from pydantic import BaseModel, Field

class RefundDto(BaseModel):
    islem_id: str = Field(..., min_length=1, max_length=30)