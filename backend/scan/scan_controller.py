from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any
from datetime import datetime
import logging

from .ocr_service import OCRService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scan", tags=["scan"])

ocr_service = OCRService()

# Known ingredients with risk levels (from your images)
KNOWN_INGREDIENTS = {
    "Kaolin": {"risk": "low", "category": "bulk"},
    "Mica": {"risk": "low", "category": "colorant"},
    "Calcium Carbonate": {"risk": "low", "category": "bulk"},
    "Fragrance": {"risk": "medium", "category": "fragrance"},
    "Dipropylene Glycol": {"risk": "low", "category": "solvent"},
    "Menthol": {"risk": "low", "category": "cooling"},
    "Niacinamide": {"risk": "low", "category": "active"},
    "Alpha-Isomethyl Ionone": {"risk": "medium", "category": "fragrance"},
    "Benzyl Alcohol": {"risk": "medium", "category": "preservative"},
    "Benzyl Salicylate": {"risk": "medium", "category": "fragrance"},
    "Cinnamyl Alcohol": {"risk": "medium", "category": "fragrance"},
    "Citronellol": {"risk": "medium", "category": "fragrance"},
    "Coumarin": {"risk": "medium", "category": "fragrance"},
    "Eugenol": {"risk": "medium", "category": "fragrance"},
    "Geraniol": {"risk": "medium", "category": "fragrance"},
    "Hexyl Cinnamal": {"risk": "medium", "category": "fragrance"},
    "Isoeugenol": {"risk": "medium", "category": "fragrance"},
    "Limonene": {"risk": "medium", "category": "fragrance"},
    "Linalool": {"risk": "medium", "category": "fragrance"},
    "Disodium Lauryl Sulfosuccinate": {"risk": "low", "category": "surfactant"},
    "Maltodextrin": {"risk": "low", "category": "bulk"},
    "Sodium Cocoyl Isethionate": {"risk": "low", "category": "surfactant"},
    "Stearic Acid": {"risk": "low", "category": "emollient"},
    "Oat Kernel Flour": {"risk": "low", "category": "bulk"},
    "Water": {"risk": "low", "category": "solvent"},
    "Cetearyl Alcohol": {"risk": "low", "category": "emollient"},
    "Paraffin": {"risk": "low", "category": "emollient"},
    "Ceteareth-6": {"risk": "low", "category": "emulsifier"},
    "Sweet Almond Oil": {"risk": "low", "category": "emollient"},
    "PEG-45 Palm Kernel Glycerides": {"risk": "low", "category": "emulsifier"},
}

@router.post("/upload")
async def scan_product_label(
    user_id: str = Form(...),
    image: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Upload and scan product label image
    """
    try:
        # Validate image
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image
        contents = await image.read()
        
        # Extract text using OCR
        extracted_text = ocr_service.extract_text_from_image(contents)
        
        # Extract ingredients from text
        ingredients = ocr_service.extract_ingredients_from_text(extracted_text)
        
        # User profile (simplified for demo)
        user_profile = {
            "skin_type": "sensitive",
            "allergies": ["fragrance"]
        }
        
        # Analyze ingredients
        analyzed_ingredients = []
        risk_counts = {"high": 0, "medium": 0, "low": 0}
        concerns = []
        
        for ing in ingredients:
            # Get ingredient info
            ing_info = KNOWN_INGREDIENTS.get(ing["name"], {
                "risk": "low", 
                "category": ing["category"]
            })
            
            risk_level = ing_info["risk"]
            
            # Check for allergies
            personalized_warnings = []
            if risk_level == "medium" and "fragrance" in user_profile.get("allergies", []):
                if ing_info["category"] == "fragrance":
                    personalized_warnings.append(f"You're allergic to fragrances! {ing['name']} may cause reaction.")
                    risk_level = "high"
            
            analyzed_ingredients.append({
                "name": ing["name"],
                "original": ing.get("original", ing["name"]),
                "category": ing_info["category"],
                "confidence": ing["confidence"],
                "risk_level": risk_level,
                "personalized_warnings": personalized_warnings
            })
            
            risk_counts[risk_level] += 1
            if personalized_warnings:
                concerns.extend(personalized_warnings)
        
        # Calculate overall safety score (0-100, higher = more risky)
        total_score = 0
        if analyzed_ingredients:
            for ing in analyzed_ingredients:
                if ing["risk_level"] == "high":
                    total_score += 80
                elif ing["risk_level"] == "medium":
                    total_score += 40
                else:
                    total_score += 10
            avg_score = total_score / len(analyzed_ingredients)
        else:
            avg_score = 0
        
        # Determine overall risk level
        if risk_counts["high"] > 0:
            overall_level = "high"
            recommendation = "⚠️ NOT RECOMMENDED - Contains ingredients you're allergic to"
        elif risk_counts["medium"] > 2 or avg_score > 30:
            overall_level = "medium"
            recommendation = "⚠️ Use with caution - Contains potential allergens"
        else:
            overall_level = "low"
            recommendation = "✅ Safe for your profile - No major concerns detected"
        
        overall_analysis = {
            "overall_level": overall_level,
            "overall_score": round(avg_score, 1),
            "high_risk_count": risk_counts["high"],
            "medium_risk_count": risk_counts["medium"],
            "low_risk_count": risk_counts["low"],
            "total_ingredients": len(analyzed_ingredients),
            "concerns": list(set(concerns))[:5],
            "recommendation": recommendation
        }
        
        return {
            "success": True,
            "extracted_text_preview": extracted_text[:300] + "..." if len(extracted_text) > 300 else extracted_text,
            "ingredients": analyzed_ingredients,
            "ingredient_count": len(analyzed_ingredients),
            "analysis": overall_analysis,
            "user_profile_applied": user_profile,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Scan failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# from fastapi import APIRouter, HTTPException, UploadFile, File, Form
# from typing import List, Dict, Any, Optional
# from datetime import datetime
# import logging

# from .ocr_service import OCRService
# from ingredients.ingredient_service import IngredientService
# from user.user_profile_service import UserProfileService

# logger = logging.getLogger(__name__)
# router = APIRouter(prefix="/scan", tags=["scan"])

# # Initialize OCR service
# ocr_service = OCRService()

# @router.post("/upload")
# async def scan_product_label(
#     user_id: str = Form(...),
#     image: UploadFile = File(...)
# ) -> Dict[str, Any]:
#     """
#     Upload and scan product label image
#     """
#     try:
#         # Validate image
#         if not image.content_type.startswith('image/'):
#             raise HTTPException(status_code=400, detail="File must be an image")
        
#         # Read image
#         contents = await image.read()
        
#         # Extract text using OpenAI Vision
#         extracted_text = ocr_service.extract_text_from_image(contents)
        
#         # Extract ingredients from text
#         ingredients = ocr_service.extract_ingredients(extracted_text)
        
#         # Get user profile
#         user_profile = UserProfileService.get_user_profile(user_id)
        
#         # Analyze each ingredient with safety data
#         analyzed_ingredients = []
#         for ing in ingredients:
#             # Get safety data
#             safety_data = IngredientService.analyze_ingredient(ing['name'])
            
#             # Calculate personalized risk
#             personalized_risk = calculate_personalized_risk(safety_data, user_profile)
            
#             analyzed_ingredients.append({
#                 "name": ing['name'],
#                 "original": ing.get('original', ing['name']),
#                 "category": ing.get('category', 'unknown'),
#                 "confidence": ing.get('confidence', 0.8),
#                 "safety": {
#                     "name": safety_data.name if safety_data else ing['name'],
#                     "description": safety_data.description if safety_data else "No data available",
#                     "risk_level": personalized_risk["level"],
#                     "risk_score": personalized_risk["score"],
#                     "benefits": safety_data.benefits if safety_data else [],
#                     "side_effects": safety_data.side_effects if safety_data else ["Insufficient data"],
#                     "personalized_warnings": personalized_risk["warnings"]
#                 } if safety_data else {
#                     "name": ing['name'],
#                     "description": "Ingredient not found in database",
#                     "risk_level": personalized_risk["level"],
#                     "risk_score": personalized_risk["score"],
#                     "benefits": [],
#                     "side_effects": ["Insufficient data"],
#                     "personalized_warnings": personalized_risk["warnings"]
#                 }
#             })
        
#         # Calculate overall product safety
#         overall_analysis = analyze_product_safety(analyzed_ingredients, user_profile)
        
#         return {
#             "success": True,
#             "extracted_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
#             "ingredients": analyzed_ingredients,
#             "ingredient_count": len(analyzed_ingredients),
#             "analysis": overall_analysis,
#             "user_profile_applied": {
#                 "skin_type": user_profile.get("skinType"),
#                 "concerns": user_profile.get("skinConcerns", []),
#                 "allergies": user_profile.get("skincareAllergies", [])
#             },
#             "timestamp": datetime.now().isoformat()
#         }
        
#     except Exception as e:
#         logger.error(f"Scan failed: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# def calculate_personalized_risk(safety_data, user_profile):
#     """Calculate personalized risk based on user profile"""
#     base_score = safety_data.risk_score if safety_data else 40
#     base_level = safety_data.risk_level if safety_data else "unknown"
#     warnings = []
    
#     ingredient_name = safety_data.name.lower() if safety_data else ""
    
#     # Check pregnancy
#     if user_profile.get("pregnancy") != "no":
#         if "retinol" in ingredient_name or "vitamin a" in ingredient_name:
#             base_score += 30
#             warnings.append("Avoid during pregnancy")
#         if "salicylic" in ingredient_name:
#             base_score += 20
#             warnings.append("Use with caution during pregnancy")
    
#     # Check sensitive skin
#     if user_profile.get("skinType") == "sensitive":
#         if "fragrance" in ingredient_name or "parfum" in ingredient_name:
#             base_score += 25
#             warnings.append("May irritate sensitive skin")
#         if "alcohol" in ingredient_name:
#             base_score += 15
#             warnings.append("Can be drying for sensitive skin")
    
#     # Check allergies
#     allergies = user_profile.get("skincareAllergies", [])
#     if "fragrance" in allergies and ("fragrance" in ingredient_name or "parfum" in ingredient_name):
#         base_score += 40
#         warnings.append("You're allergic to fragrances!")
    
#     # Determine level
#     base_score = min(100, base_score)
#     if base_score >= 70:
#         level = "high"
#     elif base_score >= 40:
#         level = "medium"
#     else:
#         level = "low"
    
#     return {
#         "score": base_score,
#         "level": level,
#         "base_level": base_level,
#         "warnings": warnings
#     }

# def analyze_product_safety(ingredients, user_profile):
#     """Analyze overall product safety"""
#     high_count = 0
#     medium_count = 0
#     low_count = 0
#     total_score = 0
#     concerns = []
    
#     for ing in ingredients:
#         risk_level = ing["safety"]["risk_level"]
#         risk_score = ing["safety"]["risk_score"]
        
#         if risk_level == "high":
#             high_count += 1
#             concerns.append(f"{ing['name']}: High risk for your profile")
#         elif risk_level == "medium":
#             medium_count += 1
#         else:
#             low_count += 1
        
#         total_score += risk_score
    
#     avg_score = total_score / len(ingredients) if ingredients else 0
    
#     # Determine overall risk
#     if high_count > 0:
#         overall_level = "high"
#         recommendation = "⚠️ Not recommended for your profile - contains high-risk ingredients"
#     elif medium_count > 2:
#         overall_level = "medium"
#         recommendation = "⚠️ Use with caution - multiple medium-risk ingredients"
#     else:
#         overall_level = "low"
#         recommendation = "✅ Appears safe for your profile"
    
#     return {
#         "overall_level": overall_level,
#         "overall_score": round(avg_score, 1),
#         "high_risk_count": high_count,
#         "medium_risk_count": medium_count,
#         "low_risk_count": low_count,
#         "total_ingredients": len(ingredients),
#         "concerns": concerns[:3],
#         "recommendation": recommendation
#     }

