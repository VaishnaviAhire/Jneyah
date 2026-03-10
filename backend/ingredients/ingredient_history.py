
from typing import List, Dict, Any, Optional
from datetime import datetime
from .ingredient_models import IngredientHistoryResponse

# In-memory storage (replace with database in production)
history_storage: List[Dict[str, Any]] = []

class IngredientHistoryService:
    
    @staticmethod
    def save_history(user_id: str, ingredient_name: str, risk_level: str = "Unknown", risk_score: int = 0, search_type: str = "manual") -> None:
        """Save ingredient search to user history"""
        history_storage.append({
            "user_id": user_id,
            "ingredient_name": ingredient_name,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "search_date": datetime.now(),
            "search_type": search_type
        })
        
        # Keep only last 100 entries per user (optional cleanup)
        user_entries = [h for h in history_storage if h["user_id"] == user_id]
        if len(user_entries) > 100:
            # Remove oldest entries
            oldest_date = sorted(user_entries, key=lambda x: x["search_date"])[0]["search_date"]
            history_storage[:] = [h for h in history_storage if not (h["user_id"] == user_id and h["search_date"] == oldest_date)]
    
    @staticmethod
    def get_user_history(user_id: str, limit: int = 20) -> List[IngredientHistoryResponse]:
        """Get user's search history"""
        user_entries = [h for h in history_storage if h["user_id"] == user_id]
        user_entries.sort(key=lambda x: x["search_date"], reverse=True)
        
        return [IngredientHistoryResponse(**entry) for entry in user_entries[:limit]]
    
    @staticmethod
    def get_recent_searches(user_id: str, limit: int = 5) -> List[str]:
        """Get recent ingredient searches for quick access"""
        user_entries = [h for h in history_storage if h["user_id"] == user_id]
        user_entries.sort(key=lambda x: x["search_date"], reverse=True)
        
        # Get unique ingredients
        seen = set()
        recent = []
        for entry in user_entries:
            if entry["ingredient_name"] not in seen:
                seen.add(entry["ingredient_name"])
                recent.append(entry["ingredient_name"])
            if len(recent) >= limit:
                break
        
        return recent
    
    @staticmethod
    def get_user_risk_pattern(user_id: str) -> Dict[str, Any]:
        """Analyze user's search pattern for risk trends"""
        user_entries = [h for h in history_storage if h["user_id"] == user_id]
        
        if not user_entries:
            return {
                "total_searches": 0,
                "high_risk_count": 0,
                "medium_risk_count": 0,
                "low_risk_count": 0,
                "most_searched_category": None
            }
        
        high_risk = sum(1 for e in user_entries if e["risk_level"].lower() == "high")
        medium_risk = sum(1 for e in user_entries if e["risk_level"].lower() == "medium")
        low_risk = sum(1 for e in user_entries if e["risk_level"].lower() == "low")
        
        return {
            "total_searches": len(user_entries),
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk,
            "high_risk_percentage": round((high_risk / len(user_entries)) * 100, 2) if len(user_entries) > 0 else 0,
            "last_search": user_entries[0]["ingredient_name"] if user_entries else None
        }


# history_storage = []

# def save_history(user_id: str, ingredient_name: str):
#     history_storage.append({
#         "user_id": user_id,
#         "ingredient": ingredient_name
#     })
