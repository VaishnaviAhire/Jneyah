

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from .ingredient_models import IngredientResponse

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "database" / "ingredient_dataset.json"

class IngredientService:
    
    @staticmethod
    def load_dataset() -> List[Dict[str, Any]]:
        """Load ingredient dataset from JSON file"""
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Return sample data if file doesn't exist
            return IngredientService.get_sample_data()
    
    @staticmethod
    def get_sample_data() -> List[Dict[str, Any]]:
        """Provide sample ingredient data for testing"""
        return [
            {
                "name": "Paraben",
                "description": "Parabens are preservatives used in cosmetics to prevent bacterial growth. They are absorbed through skin and have been found in breast cancer tissues, though direct causation hasn't been proven.",
                "risk_level": "High",
                "risk_score": 85,
                "benefits": ["Extends product shelf life", "Prevents microbial growth", "Effective preservative"],
                "side_effects": ["Skin irritation", "Allergic reactions", "Potential endocrine disruption", "May accumulate in body tissues"],
                "category": "preservatives",
                "synonyms": ["Butylparaben", "Propylparaben", "Methylparaben", "Ethylparaben"],
                "scientific_name": "4-Hydroxybenzoic acid esters",
                "regulatory_status": {
                    "fda": "Generally recognized as safe in low concentrations",
                    "eu": "Restricted in cosmetics"
                },
                "safe_concentration": "Less than 0.4% for single ester",
                "common_uses": ["Shampoos", "Moisturizers", "Makeup"],
                "alternatives": ["Phenoxyethanol", "Potassium sorbate"]
            },
            {
                "name": "Vitamin C",
                "description": "Vitamin C (Ascorbic Acid) is a powerful antioxidant that brightens skin, boosts collagen production, and protects against environmental damage.",
                "risk_level": "Low",
                "risk_score": 15,
                "benefits": ["Brightens skin", "Boosts collagen", "Antioxidant protection", "Reduces hyperpigmentation"],
                "side_effects": ["Mild tingling", "Oxidizes quickly", "May cause irritation in high concentrations"],
                "category": "actives",
                "synonyms": ["Ascorbic Acid", "L-Ascorbic Acid"],
                "scientific_name": "L-ascorbic acid",
                "regulatory_status": {
                    "fda": "GRAS",
                    "eu": "Approved"
                },
                "safe_concentration": "5-20% for skincare",
                "common_uses": ["Serums", "Moisturizers", "Sunscreens"],
                "alternatives": ["Vitamin E", "Ferulic Acid"]
            },
            {
                "name": "Retinol",
                "description": "Retinol is a vitamin A derivative that accelerates skin cell turnover and stimulates collagen production for anti-aging benefits.",
                "risk_level": "Medium",
                "risk_score": 55,
                "benefits": ["Reduces fine lines", "Improves skin texture", "Unclogs pores", "Boosts collagen"],
                "side_effects": ["Initial purging", "Dryness and peeling", "Sun sensitivity", "Not safe during pregnancy"],
                "category": "actives",
                "synonyms": ["Vitamin A", "Retinyl Palmitate"],
                "scientific_name": "Retinol",
                "regulatory_status": {
                    "fda": "Approved for OTC use",
                    "eu": "Restricted concentration"
                },
                "safe_concentration": "0.01% to 1%",
                "common_uses": ["Anti-aging creams", "Serums", "Acne treatments"],
                "alternatives": ["Bakuchiol", "Granactive Retinoid"]
            },
            {
                "name": "Hyaluronic Acid",
                "description": "Hyaluronic Acid is a humectant that attracts and retains moisture, keeping skin hydrated and plump.",
                "risk_level": "Low",
                "risk_score": 5,
                "benefits": ["Deep hydration", "Plumps skin", "Reduces fine lines", "Suitable for all skin types"],
                "side_effects": ["Rare irritation", "May pill with other products"],
                "category": "humectants",
                "synonyms": ["HA", "Sodium Hyaluronate"],
                "scientific_name": "Hyaluronic acid",
                "regulatory_status": {
                    "fda": "GRAS",
                    "eu": "Approved"
                },
                "safe_concentration": "0.1% to 2%",
                "common_uses": ["Serums", "Moisturizers", "Sheet masks"],
                "alternatives": ["Glycerin", "Sodium PCA"]
            },
            {
                "name": "Niacinamide",
                "description": "Niacinamide (Vitamin B3) helps build proteins in the skin and locks in moisture to prevent environmental damage.",
                "risk_level": "Low",
                "risk_score": 10,
                "benefits": ["Reduces inflammation", "Minimizes pores", "Regulates oil", "Brightens skin"],
                "side_effects": ["Mild flushing in high concentrations"],
                "category": "actives",
                "synonyms": ["Vitamin B3", "Nicotinamide"],
                "scientific_name": "Niacinamide",
                "regulatory_status": {
                    "fda": "GRAS",
                    "eu": "Approved"
                },
                "safe_concentration": "2-10%",
                "common_uses": ["Serums", "Moisturizers", "Toners"],
                "alternatives": ["Vitamin C", "Alpha Arbutin"]
            },
            {
                "name": "Fragrance",
                "description": "Fragrance in products can be synthetic or natural and is often a mix of many chemicals. Common allergen for many people.",
                "risk_level": "Medium",
                "risk_score": 60,
                "benefits": ["Pleasant scent", "Enhances user experience"],
                "side_effects": ["Allergic reactions", "Contact dermatitis", "Headaches"],
                "category": "fragrances",
                "synonyms": ["Parfum", "Aroma"],
                "scientific_name": "Varies",
                "regulatory_status": {
                    "fda": "Requires label declaration",
                    "eu": "26 allergens must be declared"
                },
                "safe_concentration": "0.5-3%",
                "common_uses": ["Perfumes", "Lotions", "Cleaning products"],
                "alternatives": ["Fragrance-free", "Essential oils"]
            }
        ]
    
    @staticmethod
    def analyze_ingredient(name: str) -> IngredientResponse:
        """Analyze an ingredient and return detailed information"""
        dataset = IngredientService.load_dataset()
        name_lower = name.lower().strip()
        
        # Check for exact match
        for item in dataset:
            if item["name"].lower() == name_lower:
                return IngredientResponse(**item)
        
        # Check for partial match
        for item in dataset:
            if name_lower in item["name"].lower():
                return IngredientResponse(**item)
        
        # Check synonyms
        for item in dataset:
            synonyms = [s.lower() for s in item.get("synonyms", [])]
            if name_lower in synonyms:
                return IngredientResponse(**item)
        
        # If not found, return default response
        return IngredientResponse(
            name=name,
            description="Ingredient not found in database. This ingredient may be new, rare, or a trade name. Please consult with a dermatologist for more information.",
            risk_level="Unknown",
            risk_score=40,
            benefits=["Information not available in database"],
            side_effects=["Insufficient scientific data available"],
            category="unknown",
            synonyms=[],
            scientific_name="Unknown",
            regulatory_status={},
            safe_concentration="Unknown",
            common_uses=[],
            alternatives=[]
        )
    
    @staticmethod
    def search_suggestions(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get search suggestions based on partial input"""
        dataset = IngredientService.load_dataset()
        suggestions = []
        
        if not query:
            return suggestions
        
        query_lower = query.lower()
        
        for item in dataset:
            if query_lower in item["name"].lower():
                suggestions.append({
                    "name": item["name"],
                    "risk_level": item["risk_level"],
                    "category": item.get("category", "unknown")
                })
            
            if len(suggestions) >= limit:
                break
        
        return suggestions


# from typing import Dict, Any, List, Optional
# import json
# from pathlib import Path

# class IngredientService:
    
#     @staticmethod
#     def analyze_ingredient(name: str) -> Optional[Dict[str, Any]]:
#         """
#         Analyze an ingredient and return safety data
#         """
#         # Mock data for testing
#         ingredients_db = {
#             "water": {
#                 "name": "Water",
#                 "description": "Universal solvent",
#                 "risk_level": "low",
#                 "risk_score": 5,
#                 "benefits": ["Hydration", "Solvent"],
#                 "side_effects": []
#             },
#             "glycerin": {
#                 "name": "Glycerin",
#                 "description": "Humectant that attracts moisture",
#                 "risk_level": "low",
#                 "risk_score": 5,
#                 "benefits": ["Hydration", "Skin barrier support"],
#                 "side_effects": ["May feel sticky in high humidity"]
#             },
#             "fragrance": {
#                 "name": "Fragrance",
#                 "description": "Scent compound",
#                 "risk_level": "medium",
#                 "risk_score": 60,
#                 "benefits": ["Pleasant scent"],
#                 "side_effects": ["Allergic reactions", "Skin irritation"]
#             },
#             "retinol": {
#                 "name": "Retinol",
#                 "description": "Vitamin A derivative for anti-aging",
#                 "risk_level": "medium",
#                 "risk_score": 55,
#                 "benefits": ["Reduces fine lines", "Boosts collagen"],
#                 "side_effects": ["Dryness", "Peeling", "Sun sensitivity"]
#             },
#             "paraben": {
#                 "name": "Paraben",
#                 "description": "Preservative",
#                 "risk_level": "high",
#                 "risk_score": 85,
#                 "benefits": ["Prevents bacterial growth"],
#                 "side_effects": ["Endocrine disruption concerns", "Skin irritation"]
#             }
#         }
        
#         name_lower = name.lower()
#         for key, data in ingredients_db.items():
#             if key in name_lower or name_lower in key:
#                 # Return as a simple object with dict() method
#                 class SimpleResponse:
#                     def __init__(self, data):
#                         self.__dict__.update(data)
#                     def dict(self):
#                         return self.__dict__
                
#                 return SimpleResponse(data)
        
#         # Return unknown ingredient
#         class SimpleResponse:
#             def __init__(self):
#                 self.name = name
#                 self.description = "Ingredient not found in database"
#                 self.risk_level = "unknown"
#                 self.risk_score = 40
#                 self.benefits = []
#                 self.side_effects = ["Insufficient data"]
#             def dict(self):
#                 return self.__dict__
        
#         return SimpleResponse()

