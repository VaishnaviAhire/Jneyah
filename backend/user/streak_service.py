from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import logging
import random
from collections import defaultdict

from .streak_models import (
    UserActivity, UserStreak, UserBadge, UserPoints, 
    HabitAlert, EcoScore, DailyChallenge, ActivityType, 
    StreakType, BadgeLevel
)

logger = logging.getLogger(__name__)

class StreakService:
    
    # Points configuration
    POINTS_CONFIG = {
        ActivityType.WATER_INTAKE: 5,
        ActivityType.HEALTHY_FOOD: 10,
        ActivityType.SAFE_PRODUCT: 15,
        ActivityType.PRODUCT_SCAN: 5,
        ActivityType.INGREDIENT_LEARN: 3,
        ActivityType.ECO_CHOICE: 20,
        ActivityType.RECYCLE: 15,
        ActivityType.REVIEW_WRITTEN: 8,
        ActivityType.COMMUNITY_SHARE: 10
    }

    # Eco points multiplier
    ECO_MULTIPLIER = 2

    # Badge definitions
    BADGES = {
        "water_beginner": {
            "name": "💧 Hydration Starter",
            "description": "Logged water intake for 3 days",
            "icon": "💧",
            "requirement": {"type": "streak", "streak_type": "water", "count": 3}
        },
        "water_master": {
            "name": "💧 Hydration Master",
            "description": "7-day water tracking streak",
            "icon": "💦",
            "requirement": {"type": "streak", "streak_type": "water", "count": 7}
        },
        "water_legend": {
            "name": "💧 Hydration Legend",
            "description": "30-day water tracking streak",
            "icon": "🌊",
            "requirement": {"type": "streak", "streak_type": "water", "count": 30}
        },
        "food_beginner": {
            "name": "🥗 Conscious Eater",
            "description": "Logged 5 healthy food choices",
            "icon": "🥗",
            "requirement": {"type": "activity", "activity_type": "healthy_food", "count": 5}
        },
        "food_explorer": {
            "name": "🍎 Food Label Pro",
            "description": "Scanned 10 food products",
            "icon": "🏷️",
            "requirement": {"type": "activity", "activity_type": "product_scan", "count": 10}
        },
        "safe_choice_beginner": {
            "name": "🧴 Safe Choice Beginner",
            "description": "7 days of safe product choices",
            "icon": "✅",
            "requirement": {"type": "streak", "streak_type": "safe_choice", "count": 7}
        },
        "safe_choice_master": {
            "name": "🛡️ Ingredient Guardian",
            "description": "30 days of safe product choices",
            "icon": "🛡️",
            "requirement": {"type": "streak", "streak_type": "safe_choice", "count": 30}
        },
        "eco_beginner": {
            "name": "🌱 Eco Starter",
            "description": "Made 3 eco-friendly choices",
            "icon": "🌱",
            "requirement": {"type": "activity", "activity_type": "eco_choice", "count": 3}
        },
        "eco_warrior": {
            "name": "♻️ Eco Warrior",
            "description": "50+ eco points earned",
            "icon": "🌍",
            "requirement": {"type": "points", "category": "eco", "points": 50}
        },
        "learning_beginner": {
            "name": "📚 Ingredient Aware",
            "description": "Learned about 10 ingredients",
            "icon": "📚",
            "requirement": {"type": "activity", "activity_type": "ingredient_learn", "count": 10}
        },
        "learning_expert": {
            "name": "🧪 Ingredient Scientist",
            "description": "Learned about 50 ingredients",
            "icon": "🔬",
            "requirement": {"type": "activity", "activity_type": "ingredient_learn", "count": 50}
        },
        "community_beginner": {
            "name": "🤝 Community Member",
            "description": "Shared in community",
            "icon": "🤝",
            "requirement": {"type": "activity", "activity_type": "community_share", "count": 1}
        },
        "reviewer": {
            "name": "✍️ Product Reviewer",
            "description": "Wrote 5 product reviews",
            "icon": "✍️",
            "requirement": {"type": "activity", "activity_type": "review_written", "count": 5}
        },
        "perfect_week": {
            "name": "⭐ Perfect Week",
            "description": "Completed all daily challenges for a week",
            "icon": "🌟",
            "requirement": {"type": "special", "condition": "perfect_week"}
        }
    }

    # In-memory storage (replace with database)
    _activities = defaultdict(list)
    _streaks = {}
    _badges = defaultdict(list)
    _points = {}
    _eco_scores = {}
    _alerts = defaultdict(list)
    _challenges = {}

    def __init__(self):
        self._init_daily_challenges()

    def _init_daily_challenges(self):
        """Initialize daily challenges"""
        today = datetime.now()
        self._challenges = {
            "1": DailyChallenge(
                challenge_id="1",
                title="💧 Hydration Check",
                description="Log your water intake today",
                points=10,
                eco_points=0,
                activity_type=ActivityType.WATER_INTAKE,
                expires_at=today + timedelta(days=1)
            ),
            "2": DailyChallenge(
                challenge_id="2",
                title="🥗 Healthy Choice",
                description="Scan a healthy food product",
                points=15,
                eco_points=5,
                activity_type=ActivityType.HEALTHY_FOOD,
                expires_at=today + timedelta(days=1)
            ),
            "3": DailyChallenge(
                challenge_id="3",
                title="🧴 Safe Product",
                description="Choose a product with low-risk ingredients",
                points=20,
                eco_points=10,
                activity_type=ActivityType.SAFE_PRODUCT,
                expires_at=today + timedelta(days=1)
            ),
            "4": DailyChallenge(
                challenge_id="4",
                title="♻️ Eco Choice",
                description="Choose a product with eco-friendly packaging",
                points=25,
                eco_points=25,
                activity_type=ActivityType.ECO_CHOICE,
                expires_at=today + timedelta(days=1)
            ),
            "5": DailyChallenge(
                challenge_id="5",
                title="📚 Learn Something New",
                description="Explore a new ingredient",
                points=5,
                eco_points=0,
                activity_type=ActivityType.INGREDIENT_LEARN,
                expires_at=today + timedelta(days=1)
            )
        }

    async def log_activity(self, user_id: str, activity_type: ActivityType, 
                          description: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Log a user activity and award points"""
        
        # Get points for activity
        base_points = self.POINTS_CONFIG.get(activity_type, 1)
        eco_points = base_points * self.ECO_MULTIPLIER if activity_type in [
            ActivityType.ECO_CHOICE, ActivityType.RECYCLE
        ] else 0

        # Create activity
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            points=base_points,
            description=description,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self._activities[user_id].append(activity)

        # Update points
        points = await self._update_user_points(user_id, base_points, eco_points, activity_type)

        # Update streaks
        streak_update = await self._update_streak(user_id, activity_type)

        # Check for badges
        new_badges = await self._check_badges(user_id)

        # Check for habit alerts
        alerts = await self._check_habit_alerts(user_id, activity_type)

        # Update eco score
        eco_update = await self._update_eco_score(user_id, activity_type, metadata)

        return {
            "activity": activity.dict(),
            "points_earned": base_points,
            "eco_points_earned": eco_points,
            "total_points": points.total_points,
            "eco_score": eco_update["total_eco_score"],
            "streak_update": streak_update,
            "new_badges": new_badges,
            "alerts": alerts,
            "level_up": points.level > (self._points.get(user_id, UserPoints(user_id=user_id)).level if user_id in self._points else 1)
        }

    async def _update_user_points(self, user_id: str, points: int, eco_points: int, 
                                  activity_type: ActivityType) -> UserPoints:
        """Update user's points"""
        if user_id not in self._points:
            self._points[user_id] = UserPoints(user_id=user_id)

        user_points = self._points[user_id]
        
        # Update category points
        if activity_type in [ActivityType.ECO_CHOICE, ActivityType.RECYCLE]:
            user_points.eco_points += eco_points
        elif activity_type in [ActivityType.WATER_INTAKE, ActivityType.HEALTHY_FOOD]:
            user_points.health_points += points
        elif activity_type in [ActivityType.SAFE_PRODUCT, ActivityType.PRODUCT_SCAN]:
            user_points.safety_points += points
        elif activity_type in [ActivityType.COMMUNITY_SHARE, ActivityType.REVIEW_WRITTEN]:
            user_points.community_points += points

        user_points.total_points += points
        user_points.last_updated = datetime.now()

        # Calculate level (every 100 points = level up)
        new_level = (user_points.total_points // 100) + 1
        if new_level > user_points.level:
            user_points.level = new_level
            user_points.points_to_next_level = (user_points.level * 100) - user_points.total_points

        return user_points

    async def _update_streak(self, user_id: str, activity_type: ActivityType) -> Dict[str, Any]:
        """Update user streaks"""
        streak_type = self._get_streak_type(activity_type)
        today = date.today()
        
        streak_key = f"{user_id}_{streak_type}"
        
        if streak_key not in self._streaks:
            self._streaks[streak_key] = UserStreak(
                user_id=user_id,
                streak_type=streak_type
            )

        streak = self._streaks[streak_key]
        
        # Check if last activity was yesterday
        if streak.last_activity_date == today - timedelta(days=1):
            streak.current_count += 1
            streak.multiplier = min(2.0, 1.0 + (streak.current_count * 0.05))  # Max 2x multiplier
        elif streak.last_activity_date == today:
            # Already logged today, don't increase
            pass
        else:
            # Streak broken
            if streak.current_count > streak.longest_count:
                streak.longest_count = streak.current_count
            streak.current_count = 1
            streak.multiplier = 1.0

        streak.last_activity_date = today
        streak.last_updated = datetime.now()

        # Calculate streak bonus
        bonus_points = int(10 * streak.multiplier) if streak.current_count > 0 else 0

        return {
            "streak_type": streak_type.value,
            "current_streak": streak.current_count,
            "longest_streak": streak.longest_count,
            "multiplier": streak.multiplier,
            "bonus_points": bonus_points,
            "message": self._get_streak_message(streak_type, streak.current_count)
        }

    def _get_streak_type(self, activity_type: ActivityType) -> StreakType:
        """Map activity type to streak type"""
        mapping = {
            ActivityType.WATER_INTAKE: StreakType.WATER,
            ActivityType.HEALTHY_FOOD: StreakType.HEALTHY_FOOD,
            ActivityType.SAFE_PRODUCT: StreakType.SAFE_CHOICE,
            ActivityType.PRODUCT_SCAN: StreakType.ECO_SCAN,
            ActivityType.INGREDIENT_LEARN: StreakType.LEARNING,
            ActivityType.COMMUNITY_SHARE: StreakType.COMMUNITY,
            ActivityType.ECO_CHOICE: StreakType.ECO_SCAN,
            ActivityType.RECYCLE: StreakType.ECO_SCAN
        }
        return mapping.get(activity_type, StreakType.LEARNING)

    def _get_streak_message(self, streak_type: StreakType, count: int) -> str:
        """Get motivational streak message"""
        messages = {
            StreakType.WATER: [
                "💧 Great job staying hydrated!",
                "💧 Your skin thanks you for the hydration!",
                "💧 {count} day streak! Keep drinking water!"
            ],
            StreakType.HEALTHY_FOOD: [
                "🥗 Healthy choices = healthy skin!",
                "🥗 You're nourishing your body!",
                "🥗 {count} days of healthy eating!"
            ],
            StreakType.SAFE_CHOICE: [
                "🧴 Smart ingredient choices!",
                "🧴 Your skin is getting safer every day!",
                "🧴 {count} days of safe products!"
            ]
        }
        
        msg_list = messages.get(streak_type, ["Keep up the great work!"])
        msg = random.choice(msg_list)
        return msg.format(count=count) if "{count}" in msg else msg

    async def _check_badges(self, user_id: str) -> List[Dict]:
        """Check and award new badges"""
        new_badges = []
        
        for badge_id, badge_info in self.BADGES.items():
            # Check if already earned
            if any(b.badge_id == badge_id for b in self._badges[user_id]):
                continue

            earned = False
            progress = 0

            if badge_info["requirement"]["type"] == "streak":
                streak_key = f"{user_id}_{badge_info['requirement']['streak_type']}"
                if streak_key in self._streaks:
                    streak = self._streaks[streak_key]
                    progress = min(100, (streak.longest_count / badge_info['requirement']['count']) * 100)
                    if streak.longest_count >= badge_info['requirement']['count']:
                        earned = True

            elif badge_info["requirement"]["type"] == "activity":
                count = sum(1 for a in self._activities[user_id] 
                          if a.activity_type.value == badge_info['requirement']['activity_type'])
                progress = min(100, (count / badge_info['requirement']['count']) * 100)
                if count >= badge_info['requirement']['count']:
                    earned = True

            elif badge_info["requirement"]["type"] == "points":
                if user_id in self._points:
                    points = self._points[user_id]
                    category_points = getattr(points, f"{badge_info['requirement']['category']}_points", 0)
                    progress = min(100, (category_points / badge_info['requirement']['points']) * 100)
                    if category_points >= badge_info['requirement']['points']:
                        earned = True

            if earned:
                badge = UserBadge(
                    user_id=user_id,
                    badge_id=badge_id,
                    badge_name=badge_info["name"],
                    badge_description=badge_info["description"],
                    badge_icon=badge_info["icon"],
                    level=self._get_badge_level(progress),
                    earned_date=datetime.now(),
                    progress=progress
                )
                self._badges[user_id].append(badge)
                new_badges.append(badge.dict())

                # Award bonus points for badge
                await self._update_user_points(
                    user_id, 
                    points=50, 
                    eco_points=10 if "eco" in badge_id else 0,
                    activity_type=ActivityType.BADGE_EARNED
                )

        return new_badges

    def _get_badge_level(self, progress: float) -> BadgeLevel:
        """Determine badge level based on progress"""
        if progress >= 100:
            return BadgeLevel.DIAMOND
        elif progress >= 80:
            return BadgeLevel.PLATINUM
        elif progress >= 60:
            return BadgeLevel.GOLD
        elif progress >= 40:
            return BadgeLevel.SILVER
        else:
            return BadgeLevel.BRONZE

    async def _check_habit_alerts(self, user_id: str, activity_type: ActivityType) -> List[Dict]:
        """Generate gentle habit alerts"""
        alerts = []
        
        # Check for consecutive risky choices
        if activity_type == ActivityType.SAFE_PRODUCT:
            recent_activities = [a for a in self._activities[user_id][-10:] 
                               if a.activity_type == ActivityType.SAFE_PRODUCT]
            
            # Check metadata for risk level
            high_risk_count = sum(1 for a in recent_activities 
                                if a.metadata.get("risk_level") == "high")
            
            if high_risk_count >= 5:
                alert = HabitAlert(
                    user_id=user_id,
                    alert_type="high_risk_pattern",
                    message="You've used products with strong fragrance 5 days in a row. Sensitive skin may react.",
                    severity="gentle",
                    created_at=datetime.now(),
                    action_needed="Try fragrance-free alternatives tomorrow"
                )
                self._alerts[user_id].append(alert)
                alerts.append(alert.dict())

        # Check for water intake
        if activity_type != ActivityType.WATER_INTAKE:
            last_water = [a for a in self._activities[user_id][-20:] 
                         if a.activity_type == ActivityType.WATER_INTAKE]
            
            if not last_water or (datetime.now() - last_water[-1].timestamp).days > 1:
                alert = HabitAlert(
                    user_id=user_id,
                    alert_type="water_reminder",
                    message="💧 Did you drink enough water today? Hydration is key for healthy skin!",
                    severity="info",
                    created_at=datetime.now(),
                    action_needed="Log your water intake"
                )
                self._alerts[user_id].append(alert)
                alerts.append(alert.dict())

        return alerts

    async def _update_eco_score(self, user_id: str, activity_type: ActivityType, 
                                metadata: Optional[Dict]) -> Dict[str, Any]:
        """Update user's eco score"""
        if user_id not in self._eco_scores:
            self._eco_scores[user_id] = EcoScore(user_id=user_id)

        eco = self._eco_scores[user_id]

        if activity_type == ActivityType.ECO_CHOICE:
            eco.sustainable_choices += 1
            eco.total_eco_score += 20
            if metadata:
                if metadata.get("recyclable"):
                    eco.recyclable_products += 1
                if metadata.get("plastic_free"):
                    eco.plastic_free += 1
                if metadata.get("organic"):
                    eco.organic_certified += 1
                if metadata.get("cruelty_free"):
                    eco.cruelty_free += 1

        elif activity_type == ActivityType.RECYCLE:
            eco.total_eco_score += 15
            eco.recyclable_products += 1

        # Calculate carbon footprint (simplified)
        total_choices = eco.sustainable_choices + eco.recyclable_products
        if total_choices > 50:
            eco.carbon_footprint = "low"
        elif total_choices > 20:
            eco.carbon_footprint = "average"
        else:
            eco.carbon_footprint = "high"

        eco.last_updated = datetime.now()

        return eco.dict()

    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get complete user dashboard data"""
        
        # Get or create points
        if user_id not in self._points:
            self._points[user_id] = UserPoints(user_id=user_id)

        points = self._points[user_id]
        
        # Get eco score
        eco = self._eco_scores.get(user_id, EcoScore(user_id=user_id))

        # Get streaks
        streaks = []
        for streak_type in StreakType:
            streak_key = f"{user_id}_{streak_type}"
            if streak_key in self._streaks:
                streaks.append(self._streaks[streak_key].dict())

        # Get badges
        badges = [b.dict() for b in self._badges[user_id]]

        # Get recent activities
        recent_activities = [a.dict() for a in self._activities[user_id][-20:]]

        # Get active alerts
        active_alerts = [a.dict() for a in self._alerts[user_id] if not a.read][-5:]

        # Get daily challenges
        challenges = [c.dict() for c in self._challenges.values() if c.is_active]

        # Calculate next level progress
        next_level_points = points.level * 100
        progress_to_next = (points.total_points % 100) / 100 * 100

        return {
            "user_id": user_id,
            "points": points.dict(),
            "eco_score": eco.dict(),
            "streaks": streaks,
            "badges": badges,
            "recent_activities": recent_activities,
            "active_alerts": active_alerts,
            "daily_challenges": challenges,
            "level_progress": {
                "current_level": points.level,
                "current_points": points.total_points,
                "points_to_next": next_level_points - points.total_points,
                "progress_percentage": progress_to_next
            },
            "stats": {
                "total_activities": len(self._activities[user_id]),
                "total_badges": len(badges),
                "current_streaks": len([s for s in streaks if s["current_count"] > 0]),
                "eco_rank": self._get_eco_rank(eco.total_eco_score)
            }
        }

    def _get_eco_rank(self, score: int) -> str:
        """Get eco rank based on score"""
        if score >= 200:
            return "🌍 Earth Guardian"
        elif score >= 100:
            return "🌱 Eco Warrior"
        elif score >= 50:
            return "♻️ Green Starter"
        else:
            return "🌿 Eco Learner"

    async def log_water_intake(self, user_id: str) -> Dict[str, Any]:
        """Quick log water intake"""
        return await self.log_activity(
            user_id=user_id,
            activity_type=ActivityType.WATER_INTAKE,
            description="💧 Drank water today",
            metadata={"source": "quick_log"}
        )

    async def check_expiring_products(self, user_id: str, products: List[Dict]) -> List[HabitAlert]:
        """Check for expiring products and create alerts"""
        alerts = []
        
        for product in products:
            if "expiry_date" in product:
                expiry = datetime.fromisoformat(product["expiry_date"])
                days_left = (expiry - datetime.now()).days
                
                if 0 < days_left <= 30:
                    alert = HabitAlert(
                        user_id=user_id,
                        alert_type="product_expiring",
                        message=f"⚠️ '{product['name']}' expires in {days_left} days",
                        severity="info",
                        created_at=datetime.now(),
                        action_needed="Use before expiry or check if still good"
                    )
                    self._alerts[user_id].append(alert)
                    alerts.append(alert)

        return alerts

    async def get_leaderboard(self, category: str = "total_points", limit: int = 10) -> List[Dict]:
        """Get leaderboard for different categories"""
        leaderboard = []
        
        for user_id, points in self._points.items():
            if category == "total_points":
                score = points.total_points
            elif category == "eco_points":
                score = points.eco_points
            elif category == "safety_points":
                score = points.safety_points
            elif category == "health_points":
                score = points.health_points
            else:
                score = points.total_points

            leaderboard.append({
                "user_id": user_id,
                "score": score,
                "level": points.level
            })

        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        return leaderboard[:limit]

    async def get_streak_calendar(self, user_id: str, streak_type: StreakType, days: int = 30) -> List[Dict]:
        """Get calendar data for streak visualization"""
        calendar = []
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        streak_key = f"{user_id}_{streak_type}"
        streak = self._streaks.get(streak_key)

        for i in range(days):
            date = start_date + timedelta(days=i)
            activity = any(
                a for a in self._activities[user_id]
                if self._get_streak_type(a.activity_type) == streak_type
                and a.timestamp.date() == date
            )

            calendar.append({
                "date": date.isoformat(),
                "active": activity,
                "streak_day": streak.current_count if streak and streak.last_activity_date == date else 0
            })

        return calendar