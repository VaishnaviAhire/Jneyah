from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class HabitEngine:
    
    @staticmethod
    def get_ingredient_insights(user_id: str, ingredient_name: str) -> Dict[str, Any]:
        """
        Get personalized insights based on user's habits
        """
        # Get user's search history and patterns
        user_patterns = HabitEngine._analyze_user_patterns(user_id)
        
        # Get ingredient frequency in user's history
        frequency = HabitEngine._get_ingredient_frequency(user_id, ingredient_name)
        
        # Generate insights
        insights = []
        recommendations = []
        
        if frequency > 5:
            insights.append(f"You've searched for {ingredient_name} {frequency} times recently")
            insights.append("You seem very interested in this ingredient")
            recommendations.append("Consider trying products with this ingredient if you haven't already")
        
        if user_patterns["common_categories"]:
            if ingredient_name in HabitEngine._get_category_ingredients(user_patterns["common_categories"][0]):
                insights.append(f"This ingredient is in your frequently searched category: {user_patterns['common_categories'][0]}")
        
        # Time-based insights
        hour = datetime.now().hour
        if 20 <= hour <= 23:
            insights.append("Evening is a great time to apply active ingredients like retinol")
        elif 6 <= hour <= 9:
            insights.append("Morning is ideal for Vitamin C and antioxidants")
        
        return {
            "frequency": frequency,
            "insights": insights,
            "recommendations": recommendations,
            "first_time_search": frequency == 0,
            "user_category_match": user_patterns["common_categories"][0] if user_patterns["common_categories"] else None
        }
    
    @staticmethod
    def _analyze_user_patterns(user_id: str) -> Dict[str, Any]:
        """
        Analyze user's search patterns
        In production, this would analyze actual user data
        """
        # Simulated data
        return {
            "common_categories": ["actives", "humectants"],
            "search_frequency": "weekly",
            "preferred_risk_level": "low",
            "last_active": datetime.now() - timedelta(days=2)
        }
    
    @staticmethod
    def _get_ingredient_frequency(user_id: str, ingredient_name: str) -> int:
        """
        Get how often user has searched for this ingredient
        """
        # Simulated data
        frequencies = {
            "user_123": {
                "Retinol": 3,
                "Vitamin C": 5,
                "Hyaluronic Acid": 2
            }
        }
        
        user_freq = frequencies.get(user_id, {})
        return user_freq.get(ingredient_name, 0)
    
    @staticmethod
    def _get_category_ingredients(category: str) -> List[str]:
        """
        Get ingredients in a category
        """
        categories = {
            "actives": ["Vitamin C", "Retinol", "Niacinamide", "Alpha Arbutin", "Azelaic Acid"],
            "humectants": ["Hyaluronic Acid", "Glycerin", "Sodium PCA", "Panthenol"],
            "preservatives": ["Paraben", "Phenoxyethanol", "Potassium Sorbate"],
            "surfactants": ["SLS", "SLES", "Cocamidopropyl Betaine"]
        }
        
        return categories.get(category, [])