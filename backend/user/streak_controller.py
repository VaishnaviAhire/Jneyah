from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime

from .streak_service import StreakService
from .streak_models import ActivityType

# Remove this problematic import
# from citizen_mode.chatbot_controller import router as chatbot_router

router = APIRouter(prefix="/streak", tags=["streaks"])

# Initialize service
streak_service = StreakService()

@router.post("/activity/log")
async def log_activity(
    user_id: str,
    activity_type: ActivityType,
    description: str,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """Log a user activity"""
    try:
        result = await streak_service.log_activity(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            metadata=metadata
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/water/log")
async def log_water(user_id: str) -> Dict[str, Any]:
    """Quick log water intake"""
    try:
        result = await streak_service.log_water_intake(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/{user_id}")
async def get_dashboard(user_id: str) -> Dict[str, Any]:
    """Get user's complete streak dashboard"""
    try:
        dashboard = await streak_service.get_user_dashboard(user_id)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/badges/{user_id}")
async def get_user_badges(user_id: str) -> List[Dict]:
    """Get user's earned badges"""
    try:
        dashboard = await streak_service.get_user_dashboard(user_id)
        return dashboard["badges"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/streaks/{user_id}")
async def get_user_streaks(user_id: str) -> List[Dict]:
    """Get user's current streaks"""
    try:
        dashboard = await streak_service.get_user_dashboard(user_id)
        return dashboard["streaks"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/{user_id}")
async def get_user_alerts(user_id: str) -> List[Dict]:
    """Get user's active alerts"""
    try:
        dashboard = await streak_service.get_user_dashboard(user_id)
        return dashboard["active_alerts"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(user_id: str, alert_id: str) -> Dict[str, str]:
    """Mark an alert as read"""
    # Implementation would mark alert as read in database
    return {"status": "success", "message": "Alert marked as read"}

@router.get("/challenges")
async def get_daily_challenges() -> List[Dict]:
    """Get today's challenges"""
    try:
        # Get from service
        challenges = list(streak_service._challenges.values())
        return [c.dict() for c in challenges if c.is_active]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/challenges/{challenge_id}/complete")
async def complete_challenge(
    user_id: str,
    challenge_id: str
) -> Dict[str, Any]:
    """Complete a daily challenge"""
    try:
        if challenge_id not in streak_service._challenges:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        challenge = streak_service._challenges[challenge_id]
        
        # Log activity for challenge completion
        result = await streak_service.log_activity(
            user_id=user_id,
            activity_type=challenge.activity_type,
            description=f"Completed challenge: {challenge.title}",
            metadata={"challenge_id": challenge_id}
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaderboard")
async def get_leaderboard(
    category: str = "total_points",
    limit: int = 10
) -> List[Dict]:
    """Get leaderboard"""
    try:
        leaderboard = await streak_service.get_leaderboard(category, limit)
        return leaderboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar/{user_id}")
async def get_streak_calendar(
    user_id: str,
    streak_type: str,
    days: int = 30
) -> List[Dict]:
    """Get streak calendar data"""
    try:
        from .streak_models import StreakType
        streak_type_enum = StreakType(streak_type)
        calendar = await streak_service.get_streak_calendar(user_id, streak_type_enum, days)
        return calendar
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products/check-expiry")
async def check_product_expiry(
    user_id: str,
    products: List[Dict]
) -> List[Dict]:
    """Check for expiring products and generate alerts"""
    try:
        alerts = await streak_service.check_expiring_products(user_id, products)
        return [a.dict() for a in alerts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/eco-score/{user_id}")
async def get_eco_score(user_id: str) -> Dict[str, Any]:
    """Get user's eco score"""
    try:
        dashboard = await streak_service.get_user_dashboard(user_id)
        return dashboard["eco_score"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/eco-choice")
async def log_eco_choice(
    user_id: str,
    choice_type: str,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """Log an eco-friendly choice"""
    try:
        result = await streak_service.log_activity(
            user_id=user_id,
            activity_type=ActivityType.ECO_CHOICE,
            description=f"Made eco-friendly choice: {choice_type}",
            metadata=metadata
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))