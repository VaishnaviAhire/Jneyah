from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class CumulativeRiskService:
    
    @staticmethod
    def check_cumulative_effects(
        user_id: str, 
        ingredient_name: str,
        risk_level: str
    ) -> Dict[str, Any]:
        """
        Check cumulative effects based on user history
        In production, this would query a database of user's product usage
        """
        # This is a simplified version - in production, this would use real user data
        
        # Simulate user's recent ingredient exposure
        recent_exposures = CumulativeRiskService._get_user_recent_exposures(user_id)
        
        # Calculate cumulative risk score
        cumulative_score = CumulativeRiskService._calculate_cumulative_score(
            recent_exposures, 
            ingredient_name, 
            risk_level
        )
        
        # Generate insights
        insights = []
        recommendations = []
        
        if cumulative_score > 70:
            insights.append("High cumulative exposure detected")
            insights.append(f"You've been exposed to {len(recent_exposures)} ingredients recently")
            recommendations.append("Consider reducing the number of products you use daily")
            recommendations.append("Look for multi-functional products to reduce ingredient load")
        elif cumulative_score > 40:
            insights.append("Moderate cumulative exposure")
            insights.append("Your current product routine has moderate ingredient load")
            recommendations.append("Consider alternating between different products")
            recommendations.append("Monitor for any sensitivity reactions")
        else:
            insights.append("Low cumulative exposure")
            insights.append("Your current routine has minimal ingredient load")
            recommendations.append("Continue your current routine")
            recommendations.append("Still patch test new products")
        
        # Add ingredient-specific insights
        if risk_level.lower() == "high":
            recommendations.append(f"Limit use of {ingredient_name} to occasional use only")
        elif risk_level.lower() == "medium":
            recommendations.append(f"Use {ingredient_name} in moderation")
        
        return {
            "cumulative_score": cumulative_score,
            "exposure_level": "high" if cumulative_score > 70 else "medium" if cumulative_score > 40 else "low",
            "recent_exposures": recent_exposures[:5],  # Return last 5
            "insights": insights,
            "recommendations": recommendations,
            "weekly_exposure_count": len(recent_exposures)
        }
    
    @staticmethod
    def _get_user_recent_exposures(user_id: str) -> List[str]:
        """
        Get user's recent ingredient exposures
        In production, this would query from database
        """
        # Simulate data - in production, this would come from user's scan history
        simulated_exposures = {
            "user_123": ["Paraben", "Fragrance", "Alcohol", "SLS", "Vitamin C", "Retinol"],
            "user_456": ["Hyaluronic Acid", "Glycerin", "Niacinamide"],
            "default": ["Fragrance", "Alcohol", "Vitamin C"]
        }
        
        return simulated_exposures.get(user_id, simulated_exposures["default"])
    
    @staticmethod
    def _calculate_cumulative_score(
        recent_exposures: List[str], 
        new_ingredient: str,
        risk_level: str
    ) -> int:
        """
        Calculate cumulative risk score based on recent exposures
        """
        base_score = len(recent_exposures) * 10
        
        # Add risk level contribution
        risk_multiplier = {
            "high": 1.5,
            "medium": 1.2,
            "low": 1.0,
            "unknown": 1.1
        }.get(risk_level.lower(), 1.0)
        
        # Check for overlapping ingredients with similar concerns
        overlapping = 0
        high_risk_ingredients = ["paraben", "phthalate", "formaldehyde", "triclosan"]
        
        for exposure in recent_exposures:
            if any(risk in exposure.lower() for risk in high_risk_ingredients):
                overlapping += 1
        
        overlapping_penalty = overlapping * 5
        
        # Calculate final score
        final_score = (base_score * risk_multiplier) + overlapping_penalty
        final_score = min(100, max(0, final_score))  # Clamp between 0-100
        
        return int(final_score)



# from typing import Dict, Any, List

# def check_cumulative_effects(user_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
#     """Check cumulative effects based on user history"""
#     # This is a placeholder - implement actual cumulative risk logic
#     return {
#         'personalized_insights': [
#             'Based on your history, you frequently use products with fragrances',
#             'Consider reducing exposure to synthetic chemicals'
#         ],
#         'weekly_exposure': 'moderate',
#         'recommendations': ['Try fragrance-free alternatives']
#     }