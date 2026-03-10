from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import hashlib
import secrets
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId

from config import settings
from auth.auth_models import UserRole, Token, TokenData, UserInDB, UserCreate, UserHealthProfile
from database.db_connection import get_db

security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.db = get_db()
        # Check if we're using real MongoDB or in-memory fallback
        self.using_mongodb = isinstance(self.db, dict) == False
    
    def hash_password(self, password: str) -> str:
        """Simple password hashing using SHA256 with salt"""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${hashed}"
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        if '$' not in hashed_password:
            return False
        
        salt, stored_hash = hashed_password.split('$', 1)
        computed_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return computed_hash == stored_hash
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        data.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            email = payload.get("sub")
            user_id = payload.get("user_id")
            role = payload.get("role")
            
            if email is None or user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
            
            return TokenData(email=email, user_id=user_id, role=role)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    
    async def register_user(self, user_data: UserCreate) -> Token:
        # Check if user exists
        if self.using_mongodb:
            existing_user = self.db.users.find_one({"email": user_data.email})
        else:
            # In-memory fallback
            existing_user = None
            for user in self.db.get("users", []):
                if user.get("email") == user_data.email:
                    existing_user = user
                    break
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = self.hash_password(user_data.password)
        
        # Create user document
        user_doc = {
            "email": user_data.email,
            "full_name": user_data.full_name,
            "password": hashed_password,
            "role": UserRole.CITIZEN.value,
            "health_profile": {},
            "is_active": True,
            "is_verified": False,
            "profile_complete": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if self.using_mongodb:
            # Real MongoDB
            result = self.db.users.insert_one(user_doc)
            user_id = str(result.inserted_id)
        else:
            # In-memory fallback
            import uuid
            user_id = str(uuid.uuid4())
            user_doc["_id"] = user_id
            if "users" not in self.db:
                self.db["users"] = []
            self.db["users"].append(user_doc)
        
        # Create tokens
        access_token = self.create_access_token(
            data={
                "sub": user_data.email,
                "user_id": user_id,
                "role": UserRole.CITIZEN.value
            }
        )
        
        refresh_token = self.create_refresh_token(
            data={
                "sub": user_data.email,
                "user_id": user_id
            }
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            role=UserRole.CITIZEN,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def login_user(self, email: str, password: str) -> Token:
        if self.using_mongodb:
            user = self.db.users.find_one({"email": email})
        else:
            # In-memory fallback
            user = None
            for u in self.db.get("users", []):
                if u.get("email") == email:
                    user = u
                    break
        
        if not user or not self.verify_password(password, user.get("password", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        update_data = {"last_login": datetime.utcnow()}
        
        if self.using_mongodb:
            self.db.users.update_one(
                {"_id": user["_id"]},
                {"$set": update_data}
            )
        else:
            user.update(update_data)
        
        # Create tokens
        user_id = str(user["_id"])
        
        access_token = self.create_access_token(
            data={
                "sub": user["email"],
                "user_id": user_id,
                "role": user["role"]
            }
        )
        
        refresh_token = self.create_refresh_token(
            data={
                "sub": user["email"],
                "user_id": user_id
            }
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            role=user["role"],
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def refresh_tokens(self, refresh_token: str) -> Token:
        try:
            token_data = self.verify_token(refresh_token)
            
            if self.using_mongodb:
                try:
                    user = self.db.users.find_one({"_id": ObjectId(token_data.user_id)})
                except:
                    user = None
            else:
                user = None
                for u in self.db.get("users", []):
                    if str(u.get("_id")) == token_data.user_id:
                        user = u
                        break
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Create new access token
            access_token = self.create_access_token(
                data={
                    "sub": user["email"],
                    "user_id": str(user["_id"]),
                    "role": user["role"]
                }
            )
            
            return Token(
                access_token=access_token,
                refresh_token=refresh_token,
                role=user["role"],
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    def get_current_user(self, token: str) -> UserInDB:
        token_data = self.verify_token(token)
        
        if self.using_mongodb:
            try:
                # Try to find user by ObjectId
                user = self.db.users.find_one({"_id": ObjectId(token_data.user_id)})
            except Exception as e:
                # If ObjectId conversion fails, try by email
                user = self.db.users.find_one({"email": token_data.email})
        else:
            user = None
            for u in self.db.get("users", []):
                if str(u.get("_id")) == token_data.user_id or u.get("email") == token_data.email:
                    user = u
                    break
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Convert MongoDB ObjectId to string
        if "_id" in user:
            user["_id"] = str(user["_id"])
        
        # Ensure health_profile exists
        if "health_profile" not in user:
            user["health_profile"] = {}
        
        # Ensure profile_complete exists
        if "profile_complete" not in user:
            user["profile_complete"] = False
        
        # Convert datetime fields to strings for Pydantic
        if "created_at" in user and isinstance(user["created_at"], datetime):
            user["created_at"] = user["created_at"].isoformat()
        if "updated_at" in user and isinstance(user["updated_at"], datetime):
            user["updated_at"] = user["updated_at"].isoformat()
        if "last_login" in user and isinstance(user["last_login"], datetime):
            user["last_login"] = user["last_login"].isoformat()
        elif "last_login" not in user:
            user["last_login"] = None
        
        return UserInDB(**user)
    
    async def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        update_data = {
            "health_profile": profile_data,
            "profile_complete": True,
            "updated_at": datetime.utcnow()
        }
        
        if self.using_mongodb:
            try:
                result = self.db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": update_data}
                )
                modified = result.modified_count > 0
            except:
                # Try with string ID
                result = self.db.users.update_one(
                    {"_id": user_id},
                    {"$set": update_data}
                )
                modified = result.modified_count > 0
        else:
            modified = False
            for user in self.db.get("users", []):
                if str(user.get("_id")) == user_id:
                    user.update(update_data)
                    modified = True
                    break
        
        if not modified:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "Profile updated successfully", "profile_complete": True}

# Create singleton instance
auth_service = AuthService()