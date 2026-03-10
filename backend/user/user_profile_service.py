
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from .user_models import UserProfile, UserRole

logger = logging.getLogger(__name__)

class UserProfileService:
    
    # In-memory storage (replace with database in production)
    _profiles = {}
    _profile_history = {}

    @staticmethod
    def get_user_profile(user_id: str) -> Dict[str, Any]:
        """
        Get user profile by ID
        """
        # Return mock profile if not found (for demo)
        if user_id not in UserProfileService._profiles:
            return UserProfileService.get_mock_profile()
        
        return UserProfileService._profiles.get(user_id, {})

    @staticmethod
    def get_mock_profile() -> Dict[str, Any]:
        """
        Get mock profile for testing
        """
        return {
            "user_id": "mock_user",
            "email": "user@example.com",
            "name": "Test User",
            "role": "citizen",
            "age": 28,
            "gender": "female",
            "pregnancy": "no",
            "skinType": "sensitive",
            "skinConcerns": ["acne", "redness"],
            "sunReaction": "burns easily",
            "skincareAllergies": ["fragrance", "preservatives"],
            "foodAllergies": ["nuts"],
            "allergySeverity": "moderate",
            "specificReactions": "Breakout from coconut oil",
            "healthConditions": ["eczema"],
            "medications": "Birth control pills",
            "diet": ["vegetarian"],
            "exercise": "3-4 times",
            "smoking": "no",
            "stress": "sometimes stressed",
            "consented": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    @staticmethod
    def create_profile(user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new user profile
        """
        profile = {
            "user_id": user_id,
            **profile_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        UserProfileService._profiles[user_id] = profile
        return profile

    @staticmethod
    def update_profile(user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing profile
        """
        if user_id not in UserProfileService._profiles:
            return UserProfileService.create_profile(user_id, profile_data)
        
        UserProfileService._profiles[user_id].update(profile_data)
        UserProfileService._profiles[user_id]["updated_at"] = datetime.now().isoformat()
        
        return UserProfileService._profiles[user_id]

    @staticmethod
    def get_profile_completion(user_id: str) -> Dict[str, Any]:
        """
        Calculate profile completion percentage
        """
        profile = UserProfileService.get_user_profile(user_id)
        
        required_fields = [
            "age", "gender", "pregnancy", "skinType", "skinConcerns",
            "sunReaction", "skincareAllergies", "foodAllergies",
            "allergySeverity", "healthConditions", "medications",
            "diet", "exercise", "smoking", "stress", "consented"
        ]
        
        completed = sum(1 for field in required_fields if field in profile and profile[field])
        total = len(required_fields)
        percentage = (completed / total) * 100
        
        missing = [field for field in required_fields if field not in profile or not profile[field]]
        
        return {
            "completion_percentage": round(percentage, 1),
            "completed_fields": completed,
            "total_fields": total,
            "missing_fields": missing,
            "is_complete": percentage == 100
        }

    @staticmethod
    def get_user_risk_factors(user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's specific risk factors based on profile
        """
        profile = UserProfileService.get_user_profile(user_id)
        risk_factors = []
        
        if profile.get("pregnancy") != "no":
            risk_factors.append({
                "factor": "Pregnancy/Breastfeeding",
                "severity": "high",
                "advice": "Avoid retinol, high-dose vitamin A, and certain essential oils"
            })
        
        if profile.get("skinType") == "sensitive":
            risk_factors.append({
                "factor": "Sensitive Skin",
                "severity": "medium",
                "advice": "Avoid fragrances, alcohol, and harsh surfactants"
            })
        
        if "acne" in profile.get("skinConcerns", []):
            risk_factors.append({
                "factor": "Acne-Prone",
                "severity": "medium",
                "advice": "Avoid comedogenic ingredients like coconut oil, isopropyl myristate"
            })
        
        allergies = profile.get("skincareAllergies", [])
        if allergies:
            risk_factors.append({
                "factor": f"Allergies: {', '.join(allergies)}",
                "severity": "high",
                "advice": f"Strictly avoid {', '.join(allergies)} in products"
            })
        
        return risk_factors




# from typing import Dict, Any, Optional, List
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# class UserProfileService:
    
#     # In-memory storage (replace with database in production)
#     _profiles = {}
#     _profile_history = {}

#     @staticmethod
#     def get_user_profile(user_id: str) -> Dict[str, Any]:
#         """
#         Get user profile by ID
#         """
#         # Return mock profile if not found (for demo)
#         if user_id not in UserProfileService._profiles:
#             return UserProfileService.get_mock_profile()
        
#         return UserProfileService._profiles.get(user_id, {})

#     @staticmethod
#     def get_mock_profile() -> Dict[str, Any]:
#         """
#         Get mock profile for testing
#         """
#         return {
#             "user_id": "mock_user",
#             "age": 28,
#             "gender": "female",
#             "pregnancy": "no",
#             "skinType": "sensitive",
#             "skinConcerns": ["acne", "redness"],
#             "sunReaction": "burns easily",
#             "skincareAllergies": ["fragrance", "preservatives"],
#             "foodAllergies": ["nuts"],
#             "allergySeverity": "moderate",
#             "specificReactions": "Breakout from coconut oil",
#             "healthConditions": ["eczema"],
#             "medications": "Birth control pills",
#             "diet": ["vegetarian"],
#             "exercise": "3-4 times",
#             "smoking": "no",
#             "stress": "sometimes stressed",
#             "consented": True,
#             "created_at": datetime.now().isoformat()
#         }

#     @staticmethod
#     def create_profile(user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Create new user profile
#         """
#         profile = {
#             "user_id": user_id,
#             **profile_data,
#             "created_at": datetime.now().isoformat(),
#             "updated_at": datetime.now().isoformat()
#         }
        
#         UserProfileService._profiles[user_id] = profile
#         return profile

#     @staticmethod
#     def update_profile(user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Update existing profile
#         """
#         if user_id not in UserProfileService._profiles:
#             return UserProfileService.create_profile(user_id, profile_data)
        
#         UserProfileService._profiles[user_id].update(profile_data)
#         UserProfileService._profiles[user_id]["updated_at"] = datetime.now().isoformat()
        
#         return UserProfileService._profiles[user_id]

#     @staticmethod
#     def get_profile_completion(user_id: str) -> Dict[str, Any]:
#         """
#         Calculate profile completion percentage
#         """
#         profile = UserProfileService.get_user_profile(user_id)
        
#         required_fields = [
#             "age", "gender", "pregnancy", "skinType", "skinConcerns",
#             "sunReaction", "skincareAllergies", "foodAllergies",
#             "allergySeverity", "healthConditions", "medications",
#             "diet", "exercise", "smoking", "stress", "consented"
#         ]
        
#         completed = sum(1 for field in required_fields if field in profile and profile[field])
#         total = len(required_fields)
#         percentage = (completed / total) * 100
        
#         missing = [field for field in required_fields if field not in profile or not profile[field]]
        
#         return {
#             "completion_percentage": round(percentage, 1),
#             "completed_fields": completed,
#             "total_fields": total,
#             "missing_fields": missing,
#             "is_complete": percentage == 100
#         }

#     @staticmethod
#     def get_user_risk_factors(user_id: str) -> List[Dict[str, Any]]:
#         """
#         Get user's specific risk factors based on profile
#         """
#         profile = UserProfileService.get_user_profile(user_id)
#         risk_factors = []
        
#         if profile.get("pregnancy") != "no":
#             risk_factors.append({
#                 "factor": "Pregnancy/Breastfeeding",
#                 "severity": "high",
#                 "advice": "Avoid retinol, high-dose vitamin A, and certain essential oils"
#             })
        
#         if profile.get("skinType") == "sensitive":
#             risk_factors.append({
#                 "factor": "Sensitive Skin",
#                 "severity": "medium",
#                 "advice": "Avoid fragrances, alcohol, and harsh surfactants"
#             })
        
#         if "acne" in profile.get("skinConcerns", []):
#             risk_factors.append({
#                 "factor": "Acne-Prone",
#                 "severity": "medium",
#                 "advice": "Avoid comedogenic ingredients like coconut oil, isopropyl myristate"
#             })
        
#         allergies = profile.get("skincareAllergies", [])
#         if allergies:
#             risk_factors.append({
#                 "factor": f"Allergies: {', '.join(allergies)}",
#                 "severity": "high",
#                 "advice": f"Strictly avoid {', '.join(allergies)} in products"
#             })
        
#         return risk_factors