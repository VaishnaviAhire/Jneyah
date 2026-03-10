from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class IngredientRequest(BaseModel):
    name: str
    user_id: Optional[str] = None

class IngredientResponse(BaseModel):
    name: str
    description: str
    risk_level: str
    risk_score: int
    benefits: List[str]
    side_effects: List[str]
    category: Optional[str] = None
    synonyms: List[str] = []
    scientific_name: Optional[str] = None
    regulatory_status: Optional[Dict[str, str]] = None
    safe_concentration: Optional[str] = None
    common_uses: List[str] = []
    alternatives: List[str] = []

class IngredientHistoryRequest(BaseModel):
    user_id: str
    ingredient_name: str
    search_type: str = "manual"  # manual, scan, etc.

class IngredientHistoryResponse(BaseModel):
    user_id: str
    ingredient_name: str
    search_date: datetime
    risk_level: str
    risk_score: int

class IngredientSearchSuggestion(BaseModel):
    name: str
    risk_level: str
    category: Optional[str] = None

class IngredientCategory(BaseModel):
    name: str
    ingredients: List[str]
    description: Optional[str] = None

    
class IngredientSearchSuggestion(BaseModel):
    name: str
    risk_level: str
    category: Optional[str] = None