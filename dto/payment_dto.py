from typing import Optional
from pydantic import BaseModel, Field, validator

class PaymentDto(BaseModel):
    kk_no: str = Field(..., min_length=1)
    islem_tutar: int = Field(..., ge=0, le=999)
    islem_guvenlik_tip: str = Field(..., description="Valid operation types: '3d' or 'NS'", pattern="^(3D|NS)$")
    islem_id: str = Field('')
