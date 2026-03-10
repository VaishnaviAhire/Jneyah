from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum

class UserRole(str, Enum):
    CITIZEN = "citizen"
    EXPERT = "expert"
    ADMIN = "admin"

class UserHealthProfile(BaseModel):
    allergies: List[str] = []
    medical_conditions: List[str] = []
    skin_type: Optional[str] = None
    skin_concerns: List[str] = []
    dietary_restrictions: List[str] = []
    medication_current: List[str] = []
    age: Optional[int] = None
    gender: Optional[str] = None

class UserBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: str = Field(alias="_id")
    role: UserRole = UserRole.CITIZEN
    health_profile: UserHealthProfile = Field(default_factory=UserHealthProfile)
    is_active: bool = True
    is_verified: bool = False
    profile_complete: bool = False
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: UserRole
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[UserRole] = None