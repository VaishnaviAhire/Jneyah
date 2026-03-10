from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime
from bson import ObjectId

from auth.auth_service import auth_service, security
from auth.auth_models import UserCreate, UserLogin, Token, UserInDB, UserHealthProfile

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new citizen user"""
    return await auth_service.register_user(user_data)

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """Login user"""
    return await auth_service.login_user(login_data.email, login_data.password)

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    return await auth_service.refresh_tokens(refresh_token)
@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user information"""
    try:
        token = credentials.credentials
        user = auth_service.get_current_user(token)
        
        # Return user data
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "profile_complete": user.profile_complete,
            "health_profile": user.health_profile,
            "created_at": user.created_at
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
@router.post("/complete-profile")
async def complete_profile(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Complete user profile with comprehensive data"""
    try:
        token = credentials.credentials
        user = auth_service.get_current_user(token)
        
        form_data = await request.form()
        
        # Comprehensive profile data structure
        profile_data = {
            # Basic Information
            "age": int(form_data.get("age")) if form_data.get("age") else None,
            "gender": form_data.get("gender"),
            "weight": float(form_data.get("weight")) if form_data.get("weight") else None,
            "height": float(form_data.get("height")) if form_data.get("height") else None,
            "pregnancy_status": form_data.get("pregnancy_status"),
            "ethnicity": form_data.get("ethnicity"),
            
            # Skin Profile
            "skin_type": form_data.get("skin_type"),
            "skin_tone": form_data.get("skin_tone"),
            "skin_concerns": form_data.getlist("skin_concerns[]"),
            "skin_conditions": form_data.get("skin_conditions"),
            "sun_sensitivity": form_data.get("sun_sensitivity"),
            
            # Allergies & Sensitivities
            "allergies": form_data.getlist("allergies[]"),
            "food_allergies": form_data.getlist("food_allergies[]"),
            "allergy_severity": form_data.get("allergy_severity"),
            "specific_allergies": form_data.get("specific_allergies"),
            "sensitivity_level": form_data.get("sensitivity_level"),
            
            # Health Conditions
            "medical_conditions": form_data.getlist("medical_conditions[]"),
            "current_medications": form_data.get("current_medications"),
            "medication_history": form_data.get("medication_history"),
            "medical_procedures": form_data.get("medical_procedures"),
            "family_history": form_data.getlist("family_history[]"),
            
            # Lifestyle
            "dietary_restrictions": form_data.getlist("dietary_restrictions[]"),
            "smoking_status": form_data.get("smoking_status"),
            "alcohol_consumption": form_data.get("alcohol_consumption"),
            "exercise_frequency": form_data.get("exercise_frequency"),
            "stress_level": form_data.get("stress_level"),
            "sleep_hours": form_data.get("sleep_hours"),
            "occupation": form_data.get("occupation"),
            
            # Metadata
            "profile_completed_at": datetime.utcnow().isoformat(),
            "data_completeness_score": calculate_completeness_score(form_data)
        }
        
        result = await auth_service.update_profile(user.id, profile_data)
        return result
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )

def calculate_completeness_score(form_data):
    """Calculate how complete the profile is (0-100)"""
    required_fields = ['age', 'gender', 'skin_type']
    completed = 0
    
    for field in required_fields:
        if form_data.get(field):
            completed += 1
    
    # Additional points for optional fields
    optional_fields = [
        'allergies', 'medical_conditions', 'current_medications',
        'dietary_restrictions', 'exercise_frequency'
    ]
    
    for field in optional_fields:
        if form_data.get(field) or form_data.getlist(field + '[]'):
            completed += 0.5
    
    # Calculate percentage (max 100)
    score = min(100, (completed / (len(required_fields) + len(optional_fields) * 0.5)) * 100)
    return round(score)



@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth"}

# Simple form handlers for HTML
@router.post("/form/register")
async def form_register(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Form-based registration"""
    if password != confirm_password:
        return JSONResponse(
            status_code=400,
            content={"message": "Passwords do not match"}
        )
    
    user_data = UserCreate(
        full_name=full_name,
        email=email,
        password=password
    )
    
    try:
        token = await auth_service.register_user(user_data)
        return JSONResponse({
            "message": "Registration successful",
            "access_token": token.access_token,
            "refresh_token": token.refresh_token,
            "redirect": "/citizen/Profile.html"
        })
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.detail}
        )
    
@router.get("/debug")
async def debug_info():
    """Debug endpoint to check authentication setup"""
    return {
        "status": "auth_debug",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "register": "POST /api/auth/register",
            "login": "POST /api/auth/login", 
            "me": "GET /api/auth/me (requires Bearer token)",
            "refresh": "POST /api/auth/refresh",
            "complete_profile": "POST /api/auth/complete-profile",
            "form_register": "POST /api/auth/form/register (for HTML forms)",
            "form_login": "POST /api/auth/form/login (for HTML forms)"
        },
        "note": "Check server logs for detailed error information"
    }

@router.post("/form/login")
async def form_login(
    email: str = Form(...),
    password: str = Form(...)
):
    """Form-based login"""
    try:
        token = await auth_service.login_user(email, password)
        
        # Check if profile is complete
        user = auth_service.get_current_user(token.access_token)
        redirect_url = "/citizen/CitizenHome.html" if user.profile_complete else "/citizen/Profile.html"
        
        return JSONResponse({
            "message": "Login successful",
            "access_token": token.access_token,
            "refresh_token": token.refresh_token,
            "redirect": redirect_url
        })
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.detail}
        )