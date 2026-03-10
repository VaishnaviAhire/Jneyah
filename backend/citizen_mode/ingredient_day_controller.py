from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, List, Optional
from datetime import datetime

from .ingredient_of_day import IngredientOfDayService
from user.user_profile_service import UserProfileService
from user.streak_service import StreakService

router = APIRouter(prefix="/ingredient-day", tags=["ingredient-of-the-day"])

@router.get("/today")
async def get_ingredient_of_day(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get today's ingredient of the day"""
    try:
        ingredient = IngredientOfDayService.get_daily_ingredient()
        
        # Record view if user is logged in
        if user_id:
            IngredientOfDayService.record_interaction(user_id, ingredient["name"], "view")
            
            # Update streak for learning
            streak_service = StreakService()
            await streak_service.log_activity(
                user_id=user_id,
                activity_type="ingredient_learn",
                description=f"Checked out Ingredient of the Day: {ingredient['name']}",
                metadata={"ingredient": ingredient["name"]}
            )
        
        return {
            "success": True,
            "data": ingredient,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/random")
async def get_random_ingredient() -> Dict[str, Any]:
    """Get a random ingredient with fun facts"""
    try:
        # Force refresh to get random
        IngredientOfDayService._update_daily_ingredient()
        ingredient = IngredientOfDayService.get_daily_ingredient()
        
        return {
            "success": True,
            "data": ingredient,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ingredient_name}")
async def get_ingredient_details(ingredient_name: str) -> Dict[str, Any]:
    """Get details for a specific ingredient"""
    try:
        ingredient = IngredientOfDayService.get_ingredient_by_name(ingredient_name)
        
        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        
        return {
            "success": True,
            "data": ingredient,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{ingredient_name}/like")
async def like_ingredient(ingredient_name: str, user_id: str) -> Dict[str, Any]:
    """Like an ingredient"""
    try:
        IngredientOfDayService.record_interaction(user_id, ingredient_name, "like")
        
        # Get updated stats
        stats = IngredientOfDayService.get_ingredient_stats(ingredient_name)
        
        return {
            "success": True,
            "message": f"You liked {ingredient_name}! ❤️",
            "total_likes": stats["total_likes"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{ingredient_name}/share")
async def share_ingredient(ingredient_name: str, user_id: str) -> Dict[str, Any]:
    """Share an ingredient"""
    try:
        IngredientOfDayService.record_interaction(user_id, ingredient_name, "share")
        
        return {
            "success": True,
            "message": f"Thanks for sharing {ingredient_name}! 📤",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{ingredient_name}/save")
async def save_ingredient(ingredient_name: str, user_id: str) -> Dict[str, Any]:
    """Save ingredient to user's collection"""
    try:
        IngredientOfDayService.record_interaction(user_id, ingredient_name, "save")
        
        # In production, save to user's saved ingredients in database
        
        return {
            "success": True,
            "message": f"Saved {ingredient_name} to your collection! 📌",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/{ingredient_name}")
async def get_ingredient_stats(ingredient_name: str) -> Dict[str, Any]:
    """Get statistics for an ingredient"""
    try:
        stats = IngredientOfDayService.get_ingredient_stats(ingredient_name)
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list/all")
async def get_all_ingredients() -> List[Dict[str, Any]]:
    """Get list of all available ingredients"""
    try:
        from ingredients.ingredient_service import IngredientService
        ingredients = IngredientService.load_dataset()
        
        # Return simplified list
        return [
            {
                "name": ing["name"],
                "risk_level": ing["risk_level"],
                "category": ing.get("category", "unknown"),
                "icon": "🧪"
            }
            for ing in ingredients
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar/{month}")
async def get_ingredient_calendar(month: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get ingredients for calendar (what appeared on which dates)"""
    try:
        # In production, query database for historical data
        # For now, return mock data
        import random
        from datetime import datetime, timedelta
        
        calendar = []
        today = datetime.now()
        
        for i in range(30):
            date = today - timedelta(days=i)
            calendar.append({
                "date": date.strftime("%Y-%m-%d"),
                "ingredient": random.choice([
                    "Retinol", "Vitamin C", "Hyaluronic Acid", 
                    "Niacinamide", "Paraben", "Salicylic Acid"
                ]),
                "views": random.randint(100, 1000),
                "likes": random.randint(10, 100)
            })
        
        return calendar
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))