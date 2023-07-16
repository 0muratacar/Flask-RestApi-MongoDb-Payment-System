from typing import Optional
from pydantic import BaseModel, Field, validator

class UserDTO(BaseModel):
    userNo: str = Field(..., min_length=1)
    authCode: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    surname: str = Field(..., min_length=1)
    birthDate: str = Field(..., min_length=1)
    phoneNumber: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    selectedCard: str = Field('')
    allCards: list[str] = Field([])
    balance: int = Field(999, ge=0)
    optionalField: Optional[str] = Field(None)

    @validator('optionalField', pre=True)
    def validate_optional_field(cls, value):
        if value is not None and len(value) < 4:
            raise ValueError("Optional field must have a minimum length of 4 when provided")
        return value