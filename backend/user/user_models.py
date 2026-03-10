from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CITIZEN = "citizen"
    EXPERT = "expert"
    ADMIN = "admin"

class UserProfile(BaseModel):
    user_id: str
    email: EmailStr
    name: Optional[str] = None
    role: UserRole = UserRole.CITIZEN
    
    # About You
    age: Optional[int] = None
    gender: Optional[str] = None
    pregnancy: Optional[str] = "no"  # "no", "pregnant", "breastfeeding", "planning"
    
    # Skin
    skinType: Optional[str] = None  # "oily", "dry", "combination", "sensitive", "normal"
    skinConcerns: List[str] = []
    sunReaction: Optional[str] = None  # "burns easily", "sometimes burns", "tans easily"
    
    # Allergies
    skincareAllergies: List[str] = []
    foodAllergies: List[str] = []
    allergySeverity: Optional[str] = None  # "mild", "moderate", "severe"
    specificReactions: Optional[str] = None
    
    # Health
    healthConditions: List[str] = []
    medications: Optional[str] = None
    
    # Habits
    diet: List[str] = []
    exercise: Optional[str] = None  # "rarely", "1-2 times", "3-4 times", "daily"
    smoking: Optional[str] = None  # "no", "quit", "occasional", "yes"
    stress: Optional[str] = None  # "relaxed", "sometimes stressed", "often stressed"
    
    # Consent
    consented: bool = False
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: EmailStr
    name: Optional[str] = None
    role: UserRole
    profile_completion: float
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class ProfileUpdate(BaseModel):
    # About You
    age: Optional[int] = None
    gender: Optional[str] = None
    pregnancy: Optional[str] = None
    
    # Skin
    skinType: Optional[str] = None
    skinConcerns: Optional[List[str]] = None
    sunReaction: Optional[str] = None
    
    # Allergies
    skincareAllergies: Optional[List[str]] = None
    foodAllergies: Optional[List[str]] = None
    allergySeverity: Optional[str] = None
    specificReactions: Optional[str] = None
    
    # Health
    healthConditions: Optional[List[str]] = None
    medications: Optional[str] = None
    
    # Habits
    diet: Optional[List[str]] = None
    exercise: Optional[str] = None
    smoking: Optional[str] = None
    stress: Optional[str] = None
    
    # Consent
    consented: Optional[bool] = None