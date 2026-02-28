from pydantic import BaseModel, EmailStr
from typing import Optional

class ProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None

class ProfileResponse(ProfileBase):
    id: int
    user_id: int

    model_config = {"from_attributes": True}

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    profile: Optional[ProfileResponse] = None

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: str | None = None
