from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, date
from enum import Enum

class ActivityType(str, Enum):
    WATER_INTAKE = "water_intake"
    HEALTHY_FOOD = "healthy_food"
    SAFE_PRODUCT = "safe_product"
    PRODUCT_SCAN = "product_scan"
    INGREDIENT_LEARN = "ingredient_learn"  # This should already be there
    ECO_CHOICE = "eco_choice"
    BADGE_EARNED = "badge_earned"
    RECYCLE = "recycle"
    REVIEW_WRITTEN = "review_written"
    COMMUNITY_SHARE = "community_share"
    INGREDIENT_LIKE = "ingredient_like"  # Add this if you want to track likes
    INGREDIENT_SHARE = "ingredient_share"

class StreakType(str, Enum):
    WATER = "water"
    HEALTHY_FOOD = "healthy_food"
    SAFE_CHOICE = "safe_choice"
    ECO_SCAN = "eco_scan"
    LEARNING = "learning"
    COMMUNITY = "community"

class BadgeLevel(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class UserActivity(BaseModel):
    user_id: str
    activity_type: ActivityType
    points: int
    description: str
    timestamp: datetime
    metadata: Optional[Dict] = {}

class UserStreak(BaseModel):
    user_id: str
    streak_type: StreakType
    current_count: int = 0
    longest_count: int = 0
    last_activity_date: Optional[date] = None
    last_updated: datetime = datetime.now()
    multiplier: float = 1.0

class UserBadge(BaseModel):
    user_id: str
    badge_id: str
    badge_name: str
    badge_description: str
    badge_icon: str
    level: BadgeLevel
    earned_date: datetime
    progress: float = 100.0
    metadata: Optional[Dict] = {}

class UserPoints(BaseModel):
    user_id: str
    total_points: int = 0
    level: int = 1
    points_to_next_level: int = 100
    eco_points: int = 0
    health_points: int = 0
    safety_points: int = 0
    community_points: int = 0
    last_updated: datetime = datetime.now()

class HabitAlert(BaseModel):
    user_id: str
    alert_type: str
    message: str
    severity: str  # "info", "warning", "gentle"
    created_at: datetime
    read: bool = False
    action_needed: Optional[str] = None

class EcoScore(BaseModel):
    user_id: str
    total_eco_score: int = 0
    sustainable_choices: int = 0
    recyclable_products: int = 0
    plastic_free: int = 0
    organic_certified: int = 0
    cruelty_free: int = 0
    carbon_footprint: str = "average"  # low, average, high
    last_updated: datetime = datetime.now()

class DailyChallenge(BaseModel):
    challenge_id: str
    title: str
    description: str
    points: int
    eco_points: int
    activity_type: ActivityType
    target_count: int = 1
    expires_at: datetime
    is_active: bool = True