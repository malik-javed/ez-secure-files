from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum

class UserType(str, Enum):
    OPS = "ops"
    CLIENT = "client"

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str
    user_type: UserType = UserType.CLIENT  # Default to CLIENT
    is_verified: bool = False
    verification_token: Optional[str] = None

class UserResponse(UserBase):
    id: str
    user_type: UserType
    is_verified: bool

    class Config:
        from_attributes = True
        populate_by_name = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_type: Optional[UserType] = None

class FileCreate(BaseModel):
    filename: str
    file_type: str
    size: int
    uploaded_by: str

class FileResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    size: int
    upload_date: str
    download_url: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True 