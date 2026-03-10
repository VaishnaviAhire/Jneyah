

from fastapi import APIRouter, HTTPException, Request
from typing import List, Dict, Any
from datetime import datetime

from ingredients.ingredient_models import (
    IngredientRequest, 
    IngredientResponse,
    IngredientHistoryRequest,
    IngredientHistoryResponse,
    IngredientSearchSuggestion
)
from ingredients.ingredient_service import IngredientService
from ingredients.ingredient_history import IngredientHistoryService
from safety_engine.cumulative_risk import CumulativeRiskService
from interaction_engine.interaction_service import InteractionService
from .habit_engine import HabitEngine

router = APIRouter(prefix="/citizen", tags=["citizen"])

@router.post("/ingredient/analyze")
async def analyze_ingredient(request: IngredientRequest) -> IngredientResponse:
    """
    Analyze an ingredient and return detailed information
    """
    try:
        result = IngredientService.analyze_ingredient(request.name)
        
        # Save to history if user_id provided
        if request.user_id:
            IngredientHistoryService.save_history(
                user_id=request.user_id,
                ingredient_name=result.name,
                risk_level=result.risk_level,
                risk_score=result.risk_score
            )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingredient/analyze-with-context")
async def analyze_ingredient_with_context(
    request: IngredientRequest
) -> Dict[str, Any]:
    """
    Analyze ingredient with additional context (cumulative effects, interactions)
    """
    try:
        # Get basic analysis
        analysis = IngredientService.analyze_ingredient(request.name)
        
        # Get cumulative effects if user_id provided
        cumulative_effects = {}
        if request.user_id:
            cumulative_effects = CumulativeRiskService.check_cumulative_effects(
                user_id=request.user_id,
                ingredient_name=request.name,
                risk_level=analysis.risk_level
            )
        
        # Check for interactions with common ingredients
        interactions = InteractionService.check_common_interactions(request.name)
        
        # Get habit insights if user_id provided
        habit_insights = {}
        if request.user_id:
            habit_insights = HabitEngine.get_ingredient_insights(
                user_id=request.user_id,
                ingredient_name=request.name
            )
        
        # Combine all data
        return {
            "analysis": analysis.dict(),
            "cumulative_effects": cumulative_effects,
            "interactions": interactions,
            "habit_insights": habit_insights,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingredient/save-history")
async def save_ingredient_history(request: IngredientHistoryRequest) -> Dict[str, str]:
    """
    Save ingredient search to user history
    """
    try:
        # Get analysis to include risk info
        analysis = IngredientService.analyze_ingredient(request.ingredient_name)
        
        IngredientHistoryService.save_history(
            user_id=request.user_id,
            ingredient_name=request.ingredient_name,
            risk_level=analysis.risk_level,
            risk_score=analysis.risk_score,
            search_type=request.search_type
        )
        
        return {"status": "success", "message": "History saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ingredient/search-suggestions")
async def get_search_suggestions(query: str = "", limit: int = 10) -> List[IngredientSearchSuggestion]:
    """
    Get search suggestions for ingredients
    """
    try:
        suggestions = IngredientService.search_suggestions(query, limit)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ingredient/categories")
async def get_ingredient_categories() -> Dict[str, List[str]]:
    """
    Get ingredient categories for filtering
    """
    try:
        categories = IngredientService.get_categories()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ingredient/history/{user_id}")
async def get_user_history(user_id: str, limit: int = 20) -> List[IngredientHistoryResponse]:
    """
    Get user's ingredient search history
    """
    try:
        history = IngredientHistoryService.get_user_history(user_id, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ingredient/recent/{user_id}")
async def get_recent_searches(user_id: str, limit: int = 5) -> List[str]:
    """
    Get user's recent ingredient searches
    """
    try:
        recent = IngredientHistoryService.get_recent_searches(user_id, limit)
        return recent
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ingredient/risk-pattern/{user_id}")
async def get_user_risk_pattern(user_id: str) -> Dict[str, Any]:
    """
    Get user's risk pattern based on search history
    """
    try:
        pattern = IngredientHistoryService.get_user_risk_pattern(user_id)
        return pattern
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# from fastapi import APIRouter, HTTPException
# from ingredients.ingredient_models import IngredientRequest
# from ingredients.ingredient_service import IngredientService
# from ingredients.ingredient_history import save_history

# router = APIRouter()

# @router.post("/citizen/ingredient/analyze")
# async def analyze_ingredient(data: IngredientRequest):
#     try:
#         result = IngredientService.analyze_ingredient(data.name)

#         # Optional history save (no auth yet)
#         save_history("demo_user", data.name)

#         return result

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
