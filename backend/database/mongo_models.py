from datetime import datetime
from bson import ObjectId
from auth.auth_models import UserRole, UserHealthProfile

class UserModel:
    @staticmethod
    def user_entity(user) -> dict:
        return {
            "_id": str(user["_id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "google_id": user.get("google_id"),
            "profile_picture": user.get("profile_picture"),
            "role": user["role"],
            "health_profile": user.get("health_profile", {}),
            "is_active": user.get("is_active", True),
            "is_verified": user.get("is_verified", False),
            "created_at": user.get("created_at", datetime.utcnow()),
            "updated_at": user.get("updated_at", datetime.utcnow()),
            "last_login": user.get("last_login")
        }

    @staticmethod
    def user_collection(db):
        return db.users