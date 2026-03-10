from typing import Dict, Any, List, Optional
from ingredients.ingredient_models import IngredientResponse
import logging

logger = logging.getLogger(__name__)

class RiskScoringService:
    
    # Risk modifiers based on user profile
    PROFILE_RISK_MODIFIERS = {
        "pregnancy": {
            "retinol": {"modifier": 0.5, "reason": "Avoid during pregnancy"},
            "salicylic acid": {"modifier": 0.4, "reason": "Limit during pregnancy"},
            "vitamin a": {"modifier": 0.5, "reason": "Avoid high doses during pregnancy"},
            "hydroquinone": {"modifier": 0.5, "reason": "Avoid during pregnancy"},
            "tretinoin": {"modifier": 0.5, "reason": "Avoid during pregnancy"},
        },
        "breastfeeding": {
            "retinol": {"modifier": 0.3, "reason": "Caution while breastfeeding"},
            "salicylic acid": {"modifier": 0.2, "reason": "Limit while breastfeeding"},
        },
        "sensitive_skin": {
            "fragrance": {"modifier": 0.4, "reason": "Common irritant for sensitive skin"},
            "alcohol": {"modifier": 0.3, "reason": "Can dry and irritate sensitive skin"},
            "essential oils": {"modifier": 0.3, "reason": "May irritate sensitive skin"},
            "sodium lauryl sulfate": {"modifier": 0.4, "reason": "Harsh for sensitive skin"},
            "acids": {"modifier": 0.3, "reason": "May cause stinging on sensitive skin"},
        },
        "acne_prone": {
            "coconut oil": {"modifier": 0.3, "reason": "Can clog pores (comedogenic)"},
            "isopropyl myristate": {"modifier": 0.4, "reason": "Highly comedogenic"},
            "lanolin": {"modifier": 0.2, "reason": "May clog pores for some"},
            "silicones": {"modifier": 0.1, "reason": "May trap bacteria for some"},
        }
    }

    @staticmethod
    def calculate_personalized_risk(
        ingredient_data: IngredientResponse,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate personalized risk score based on user profile
        """
        base_risk = ingredient_data.risk_score if ingredient_data else 40
        base_level = ingredient_data.risk_level if ingredient_data else "unknown"
        
        personalized_score = base_risk
        warnings = []
        reasons = []
        
        ingredient_name = ingredient_data.name.lower() if ingredient_data else ""
        
        # Check pregnancy
        pregnancy_status = user_profile.get("pregnancy", "no")
        if pregnancy_status != "no":
            for ing, modifier in RiskScoringService.PROFILE_RISK_MODIFIERS["pregnancy"].items():
                if ing in ingredient_name:
                    personalized_score += base_risk * modifier["modifier"]
                    warnings.append(modifier["reason"])
                    reasons.append(f"Pregnancy concern: {modifier['reason']}")
        
        # Check breastfeeding
        if pregnancy_status == "breastfeeding":
            for ing, modifier in RiskScoringService.PROFILE_RISK_MODIFIERS["breastfeeding"].items():
                if ing in ingredient_name:
                    personalized_score += base_risk * modifier["modifier"]
                    warnings.append(modifier["reason"])
        
        # Check sensitive skin
        if user_profile.get("skinType") == "sensitive":
            for ing, modifier in RiskScoringService.PROFILE_RISK_MODIFIERS["sensitive_skin"].items():
                if ing in ingredient_name:
                    personalized_score += base_risk * modifier["modifier"]
                    warnings.append(modifier["reason"])
        
        # Check acne prone
        if "acne" in user_profile.get("skinConcerns", []):
            for ing, modifier in RiskScoringService.PROFILE_RISK_MODIFIERS["acne_prone"].items():
                if ing in ingredient_name:
                    personalized_score += base_risk * modifier["modifier"]
                    warnings.append(modifier["reason"])
        
        # Check allergies
        allergies = user_profile.get("skincareAllergies", [])
        if "fragrance" in allergies and any(frag in ingredient_name for frag in ["fragrance", "parfum", "limonene"]):
            personalized_score += 40
            warnings.append("You're allergic to fragrances!")
            reasons.append("Known fragrance allergy")
        
        if "preservatives" in allergies and any(pres in ingredient_name for pres in ["paraben", "formaldehyde"]):
            personalized_score += 40
            warnings.append("You're allergic to preservatives!")
            reasons.append("Known preservative allergy")
        
        # Cap at 100
        personalized_score = min(100, personalized_score)
        
        # Determine personalized level
        if personalized_score >= 70:
            personalized_level = "high"
        elif personalized_score >= 40:
            personalized_level = "medium"
        else:
            personalized_level = "low"
        
        return {
            "score": int(personalized_score),
            "level": personalized_level,
            "base_score": base_risk,
            "base_level": base_level,
            "warnings": warnings,
            "reasons": reasons,
            "personalized": True
        }

    @staticmethod
    def calculate_combination_risk(
        ingredients: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate risk from ingredient combinations
        """
        total_score = 0
        interactions = []
        
        # Check each pair
        for i in range(len(ingredients)):
            for j in range(i + 1, len(ingredients)):
                ing1 = ingredients[i]["name"].lower()
                ing2 = ingredients[j]["name"].lower()
                
                # Known problematic combinations
                if ("retinol" in ing1 or "retinol" in ing2) and \
                   ("glycolic" in ing1 or "glycolic" in ing2 or 
                    "lactic" in ing1 or "lactic" in ing2 or
                    "salicylic" in ing1 or "salicylic" in ing2):
                    interactions.append({
                        "ingredients": [ingredients[i]["name"], ingredients[j]["name"]],
                        "risk": "high",
                        "reason": "Retinol with exfoliating acids can cause severe irritation"
                    })
                    total_score += 30
                
                if ("vitamin c" in ing1 or "vitamin c" in ing2) and \
                   ("retinol" in ing1 or "retinol" in ing2):
                    interactions.append({
                        "ingredients": [ingredients[i]["name"], ingredients[j]["name"]],
                        "risk": "medium",
                        "reason": "Vitamin C and Retinol may reduce each other's effectiveness"
                    })
                    total_score += 15
        
        return {
            "combination_score": min(100, total_score),
            "interactions": interactions,
            "interaction_count": len(interactions)
        }
# from typing import Dict, Any

# def calculate_risk_score(analysis: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
#     """Calculate risk score based on analysis and user profile"""
#     concern_count = len(analysis.get('ingredients_of_concern', []))
#     total_count = analysis.get('chemical_count', 1)
    
#     risk_percentage = (concern_count / total_count) * 100
    
#     if concern_count == 0:
#         level = 'low'
#         color = 'green'
#         score = 10
#     elif risk_percentage < 20:
#         level = 'low'
#         color = 'green'
#         score = 7
#     elif risk_percentage < 50:
#         level = 'medium'
#         color = 'yellow'
#         score = 5
#     else:
#         level = 'high'
#         color = 'red'
#         score = 2
    
#     return {
#         'level': level,
#         'color': color,
#         'score': score,
#         'primary_concerns': [i['original'] for i in analysis.get('ingredients_of_concern', [])[:2]],
#         'recommendation': get_recommendation(level)
#     }

# def get_recommendation(level: str) -> str:
#     """Get recommendation based on risk level"""
#     recommendations = {
#         'low': 'This product appears safe for most users',
#         'medium': 'Use with caution, consider alternatives',
#         'high': 'Avoid this product, high risk ingredients detected'
#     }
#     return recommendations.get(level, '')