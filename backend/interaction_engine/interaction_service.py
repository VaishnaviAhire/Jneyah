from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class InteractionService:
    
    # Known ingredient interactions
    INTERACTION_DATABASE = {
        "retinol": {
            "incompatible_with": ["glycolic acid", "lactic acid", "salicylic acid", "benzoyl peroxide", "vitamin c"],
            "warning": "Can cause severe irritation when used with other exfoliants",
            "severity": "high"
        },
        "vitamin c": {
            "incompatible_with": ["retinol", "benzoyl peroxide"],
            "warning": "May be less effective when used with retinol or benzoyl peroxide",
            "severity": "medium"
        },
        "benzoyl peroxide": {
            "incompatible_with": ["retinol", "vitamin c", "tretinoin"],
            "warning": "Can cause excessive dryness and irritation",
            "severity": "high"
        },
        "salicylic acid": {
            "incompatible_with": ["retinol", "glycolic acid", "lactic acid"],
            "warning": "Using multiple exfoliants increases irritation risk",
            "severity": "high"
        },
        "glycolic acid": {
            "incompatible_with": ["retinol", "salicylic acid", "lactic acid"],
            "warning": "Over-exfoliation can damage skin barrier",
            "severity": "high"
        }
    }

    @staticmethod
    def check_interaction(ingredient1: str, ingredient2: str) -> Optional[Dict[str, Any]]:
        """
        Check interaction between two ingredients
        """
        ing1_lower = ingredient1.lower()
        ing2_lower = ingredient2.lower()
        
        # Check each ingredient against database
        for ing, data in InteractionService.INTERACTION_DATABASE.items():
            if ing in ing1_lower or ing in ing2_lower:
                for incompatible in data["incompatible_with"]:
                    if incompatible in ing1_lower or incompatible in ing2_lower:
                        return {
                            "ingredients": [ingredient1, ingredient2],
                            "type": "incompatible",
                            "warning": data["warning"],
                            "severity": data["severity"],
                            "recommendation": "Use these ingredients at different times of day"
                        }
        
        return None

    @staticmethod
    def check_multiple_interactions(ingredients: List[str]) -> Dict[str, Any]:
        """
        Check interactions among multiple ingredients
        """
        interactions = []
        high_risk_count = 0
        medium_risk_count = 0
        
        # Check each pair
        for i in range(len(ingredients)):
            for j in range(i + 1, len(ingredients)):
                interaction = InteractionService.check_interaction(
                    ingredients[i], 
                    ingredients[j]
                )
                if interaction:
                    interactions.append(interaction)
                    if interaction["severity"] == "high":
                        high_risk_count += 1
                    else:
                        medium_risk_count += 1
        
        # Check for multiple exfoliants
        exfoliants = ["glycolic", "lactic", "salicylic", "retinol", "aha", "bha"]
        exfoliant_count = sum(
            1 for ing in ingredients 
            if any(exf in ing.lower() for exf in exfoliants)
        )
        
        if exfoliant_count > 2:
            interactions.append({
                "type": "warning",
                "message": f"Multiple exfoliants detected ({exfoliant_count})",
                "severity": "high",
                "recommendation": "Risk of over-exfoliation - consider alternating products"
            })
            high_risk_count += 1
        
        # Calculate overall interaction risk
        if high_risk_count > 0:
            overall_risk = "high"
            recommendation = "Avoid using this combination of products together"
        elif medium_risk_count > 0:
            overall_risk = "medium"
            recommendation = "Use with caution and monitor skin reaction"
        else:
            overall_risk = "low"
            recommendation = "No known negative interactions detected"
        
        return {
            "has_interactions": len(interactions) > 0,
            "interactions": interactions,
            "count": len(interactions),
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "overall_risk": overall_risk,
            "recommendation": recommendation
        }

    @staticmethod
    def check_ingredient_category_interactions(
        ingredient: str,
        current_routine: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Check how a new ingredient interacts with current routine
        """
        interactions = []
        
        # Check against each ingredient in current routine
        for routine_ing in current_routine:
            interaction = InteractionService.check_interaction(ingredient, routine_ing)
            if interaction:
                interactions.append(interaction)
        
        return interactions