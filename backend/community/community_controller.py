from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime

from .community_service import CommunityService
from .community_models import PostCreate, CommentCreate, PostType, ReactionType

router = APIRouter(prefix="/community", tags=["community"])

@router.post("/posts")
async def create_post(
    user_id: str,
    post: PostCreate
) -> Dict[str, Any]:
    """Create a new post"""
    try:
        result = await CommunityService.create_post(user_id, post)
        return {
            "success": True,
            "data": result,
            "message": "Post created successfully! 🎉"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}")
async def get_post(
    post_id: str,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get a single post by ID"""
    try:
        post = await CommunityService.get_post(post_id, user_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return {
            "success": True,
            "data": post
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feed")
async def get_feed(
    user_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50)
) -> Dict[str, Any]:
    """Get community feed"""
    try:
        feed = await CommunityService.get_feed(user_id, page, limit)
        return {
            "success": True,
            "data": feed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/react")
async def react_to_post(
    post_id: str,
    user_id: str,
    reaction: ReactionType
) -> Dict[str, Any]:
    """React to a post"""
    try:
        result = await CommunityService.react_to_post(post_id, user_id, reaction)
        return {
            "success": True,
            "data": result,
            "message": f"Reacted with {reaction.value}! 💫"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/comments")
async def add_comment(
    post_id: str,
    user_id: str,
    comment: CommentCreate
) -> Dict[str, Any]:
    """Add a comment to a post"""
    try:
        result = await CommunityService.add_comment(post_id, user_id, comment)
        return {
            "success": True,
            "data": result,
            "message": "Comment added! 💬"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/save")
async def save_post(
    post_id: str,
    user_id: str
) -> Dict[str, Any]:
    """Save a post to collection"""
    try:
        result = await CommunityService.save_post(post_id, user_id)
        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/saved/{user_id}")
async def get_saved_posts(user_id: str) -> Dict[str, Any]:
    """Get user's saved posts"""
    try:
        posts = await CommunityService.get_saved_posts(user_id)
        return {
            "success": True,
            "data": posts,
            "count": len(posts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/follow/{target_user_id}")
async def follow_user(
    user_id: str,
    target_user_id: str
) -> Dict[str, Any]:
    """Follow or unfollow a user"""
    try:
        result = await CommunityService.follow_user(user_id, target_user_id)
        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending")
async def get_trending() -> Dict[str, Any]:
    """Get trending topics and posts"""
    try:
        trending = await CommunityService.get_trending()
        return {
            "success": True,
            "data": trending
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_posts(
    q: str = Query(..., min_length=2),
    type: Optional[PostType] = None
) -> Dict[str, Any]:
    """Search posts"""
    try:
        results = await CommunityService.search_posts(q, type)
        return {
            "success": True,
            "data": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/report")
async def report_post(
    post_id: str,
    user_id: str,
    reason: str,
    details: Optional[str] = None
) -> Dict[str, Any]:
    """Report a post"""
    try:
        result = await CommunityService.report_post(post_id, user_id, reason, details)
        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    user_id: str
) -> Dict[str, Any]:
    """Delete a post (author or moderator only)"""
    try:
        result = await CommunityService.delete_post(post_id, user_id)
        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=403 if "authorized" in str(e) else 404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{target_user_id}")
async def get_user_profile(
    target_user_id: str,
    viewer_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get user's community profile"""
    try:
        profile = await CommunityService.get_user_profile(target_user_id, viewer_id)
        return {
            "success": True,
            "data": profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feed/personal/{user_id}")
async def get_personal_feed(user_id: str) -> Dict[str, Any]:
    """Get personalized feed (posts from followed users)"""
    try:
        feed = await CommunityService.get_user_feed(user_id)
        return {
            "success": True,
            "data": feed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/post-types")
async def get_post_types() -> Dict[str, Any]:
    """Get available post types"""
    return {
        "success": True,
        "data": [
            {"value": pt.value, "label": pt.value.replace("_", " ").title()}
            for pt in PostType
        ]
    }

@router.get("/reaction-types")
async def get_reaction_types() -> Dict[str, Any]:
    """Get available reaction types"""
    return {
        "success": True,
        "data": [
            {"value": rt.value, "emoji": cls._get_reaction_emoji(rt)}
            for rt in ReactionType
        ]
    }

@classmethod
def _get_reaction_emoji(cls, reaction: ReactionType) -> str:
    """Get emoji for reaction type"""
    emojis = {
        ReactionType.LIKE: "👍",
        ReactionType.LOVE: "❤️",
        ReactionType.HELPFUL: "💡",
        ReactionType.LOL: "😂",
        ReactionType.WOW: "😮",
        ReactionType.SAD: "😢",
        ReactionType.ANGRY: "😠",
    }
    return emojis.get(reaction, "👍")