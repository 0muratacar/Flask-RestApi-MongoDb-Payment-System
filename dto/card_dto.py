from typing import Optional
from pydantic import BaseModel, Field, validator

class CardDto(BaseModel):
    kk_sahibi: str = Field(..., min_length=1, max_length=50)
    kk_no: str = Field(..., min_length=16, max_length=16)
    kk_sk_ay: str = Field(..., min_length=2, max_length=2)
    kk_sk_yil: str = Field(..., min_length=4, max_length=4)
    kk_kart_adi: Optional[str] = Field(None)


    @validator('kk_kart_adi', pre=True)
    def validate_optional_field(cls, value):
        if value is not None and len(value) >150:
            raise ValueError("kk_kart_adi field must have a maximum length of 150 when provided")
        return value

