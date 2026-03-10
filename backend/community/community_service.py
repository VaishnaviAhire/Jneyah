import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import logging
from collections import defaultdict

from .community_models import (
    Post, Comment, CommunityUser, PostCreate, CommentCreate,
    PostType, ReactionType, TrendingTopic, ReportPost
)
from ingredients.ingredient_service import IngredientService
from user.user_profile_service import UserProfileService
from user.streak_service import StreakService

logger = logging.getLogger(__name__)

class CommunityService:
    
    # In-memory storage (replace with database in production)
    _posts = {}
    _comments = {}
    _users = {}
    _followers = defaultdict(set)
    _following = defaultdict(set)
    _saved_posts = defaultdict(set)
    _reports = []
    _trending_cache = {}
    _last_trending_update = None
    
    # Mock user avatars
    AVATARS = [
        "https://api.dicebear.com/7.x/avataaars/svg?seed=1",
        "https://api.dicebear.com/7.x/avataaars/svg?seed=2",
        "https://api.dicebear.com/7.x/avataaars/svg?seed=3",
        "https://api.dicebear.com/7.x/avataaars/svg?seed=4",
        "https://api.dicebear.com/7.x/avataaars/svg?seed=5",
    ]
    
    # Mock badges
    BADGES = [
        "🌱 Skincare Newbie",
        "🧪 Ingredient Explorer",
        "🔬 Ingredient Scientist",
        "💧 Hydration Hero",
        "🧴 Product Guru",
        "🌍 Eco Warrior",
        "📚 Knowledge Seeker",
        "🎓 Skincare Graduate",
        "👑 Community Legend",
        "🦸‍♀️ Routine Master"
    ]

    @classmethod
    async def create_post(cls, user_id: str, post_data: PostCreate) -> Dict[str, Any]:
        """Create a new post"""
        # Get or create user profile
        user = await cls._get_or_create_user(user_id)
        
        # Generate post ID
        post_id = str(uuid.uuid4())[:8]
        
        # Create post
        post = Post(
            post_id=post_id,
            user_id=user_id,
            user_name=user["display_name"],
            user_avatar=user["avatar"],
            user_badge=user.get("badge"),
            post_type=post_data.post_type,
            title=post_data.title,
            content=post_data.content,
            images=post_data.images,
            tags=post_data.tags,
            mentioned_ingredients=post_data.mentioned_ingredients,
            mentioned_products=post_data.mentioned_products,
            is_anonymous=post_data.is_anonymous,
            created_at=datetime.now(),
            last_activity_at=datetime.now()
        )
        
        # Store post
        cls._posts[post_id] = post
        
        # Update user post count
        user["post_count"] += 1
        cls._users[user_id] = user
        
        # Award points for posting
        streak_service = StreakService()
        await streak_service.log_activity(
            user_id=user_id,
            activity_type="community_share",
            description=f"Created a {post_data.post_type.value} post",
            metadata={"post_id": post_id, "post_type": post_data.post_type.value}
        )
        
        # Update trending cache
        cls._update_trending_for_ingredients(post_data.mentioned_ingredients)
        
        return cls._format_post(post)

    @classmethod
    async def get_post(cls, post_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a single post by ID"""
        if post_id not in cls._posts:
            return None
        
        post = cls._posts[post_id]
        
        # Increment view count
        post.view_count += 1
        
        # Get user's reaction if provided
        user_reaction = None
        if user_id and user_id in post.user_reactions:
            user_reaction = post.user_reactions[user_id].value
        
        # Get comments
        comments = await cls.get_post_comments(post_id, user_id)
        
        return {
            **cls._format_post(post),
            "user_reaction": user_reaction,
            "comments": comments,
            "comment_count": len(comments),
            "saved_by_user": user_id in cls._saved_posts.get(post_id, set()) if user_id else False
        }

    @classmethod
    async def get_feed(cls, user_id: Optional[str] = None, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get feed posts"""
        start = (page - 1) * limit
        end = start + limit
        
        # Get all posts, sort by last activity
        all_posts = list(cls._posts.values())
        all_posts.sort(key=lambda x: x.last_activity_at, reverse=True)
        
        posts = all_posts[start:end]
        
        # Get user's reactions
        user_reactions = {}
        if user_id:
            for post in posts:
                if user_id in post.user_reactions:
                    user_reactions[post.post_id] = post.user_reactions[user_id].value
        
        formatted_posts = []
        for post in posts:
            formatted = cls._format_post(post)
            formatted["user_reaction"] = user_reactions.get(post.post_id)
            formatted["saved_by_user"] = user_id in cls._saved_posts.get(post.post_id, set()) if user_id else False
            formatted_posts.append(formatted)
        
        return {
            "posts": formatted_posts,
            "page": page,
            "total_pages": (len(cls._posts) + limit - 1) // limit,
            "total_posts": len(cls._posts),
            "has_next": end < len(cls._posts)
        }

    @classmethod
    async def react_to_post(cls, post_id: str, user_id: str, reaction: ReactionType) -> Dict[str, Any]:
        """Add/update reaction to a post"""
        if post_id not in cls._posts:
            raise ValueError("Post not found")
        
        post = cls._posts[post_id]
        
        # Remove old reaction if exists
        if user_id in post.user_reactions:
            old_reaction = post.user_reactions[user_id]
            post.reactions[old_reaction] = max(0, post.reactions[old_reaction] - 1)
        
        # Add new reaction
        post.user_reactions[user_id] = reaction
        post.reactions[reaction] = post.reactions.get(reaction, 0) + 1
        
        post.last_activity_at = datetime.now()
        
        # Award points for engagement
        if reaction == ReactionType.HELPFUL:
            streak_service = StreakService()
            await streak_service.log_activity(
                user_id=user_id,
                activity_type="community_share",
                description="Found a post helpful",
                metadata={"post_id": post_id, "reaction": reaction.value}
            )
        
        return {
            "post_id": post_id,
            "reaction": reaction.value,
            "reactions": {k.value: v for k, v in post.reactions.items()},
            "total_reactions": sum(post.reactions.values())
        }

    @classmethod
    async def add_comment(cls, post_id: str, user_id: str, comment_data: CommentCreate) -> Dict[str, Any]:
        """Add a comment to a post"""
        if post_id not in cls._posts:
            raise ValueError("Post not found")
        
        post = cls._posts[post_id]
        user = await cls._get_or_create_user(user_id)
        
        # Generate comment ID
        comment_id = str(uuid.uuid4())[:8]
        
        # Create comment
        comment = Comment(
            comment_id=comment_id,
            post_id=post_id,
            user_id=user_id,
            user_name=user["display_name"],
            user_avatar=user["avatar"],
            user_badge=user.get("badge"),
            content=comment_data.content,
            images=comment_data.images,
            reply_to=comment_data.reply_to,
            created_at=datetime.now()
        )
        
        # Handle replies
        if comment_data.reply_to:
            if comment_data.reply_to in cls._comments:
                parent = cls._comments[comment_data.reply_to]
                parent.replies.append(comment_id)
                parent.reply_count += 1
        
        # Store comment
        cls._comments[comment_id] = comment
        
        # Update post comment count
        post.comment_count += 1
        post.last_activity_at = datetime.now()
        
        # Update user comment count
        user["comment_count"] += 1
        cls._users[user_id] = user
        
        # Award points for commenting
        streak_service = StreakService()
        await streak_service.log_activity(
            user_id=user_id,
            activity_type="community_share",
            description="Commented on a post",
            metadata={"post_id": post_id, "comment_id": comment_id}
        )
        
        return cls._format_comment(comment)

    @classmethod
    async def get_post_comments(cls, post_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all comments for a post"""
        post_comments = [
            c for c in cls._comments.values() 
            if c.post_id == post_id and c.reply_to is None
        ]
        post_comments.sort(key=lambda x: x.created_at)
        
        result = []
        for comment in post_comments:
            comment_dict = cls._format_comment(comment)
            
            # Add replies
            if comment.replies:
                comment_dict["replies"] = [
                    cls._format_comment(cls._comments[reply_id])
                    for reply_id in comment.replies
                    if reply_id in cls._comments
                ]
            
            result.append(comment_dict)
        
        return result

    @classmethod
    async def save_post(cls, post_id: str, user_id: str) -> Dict[str, str]:
        """Save a post to user's collection"""
        if post_id not in cls._posts:
            raise ValueError("Post not found")
        
        if post_id in cls._saved_posts[user_id]:
            cls._saved_posts[user_id].remove(post_id)
            message = "Post removed from saved"
        else:
            cls._saved_posts[user_id].add(post_id)
            message = "Post saved successfully"
            
            # Award points for saving
            streak_service = StreakService()
            await streak_service.log_activity(
                user_id=user_id,
                activity_type="community_share",
                description="Saved a post for later",
                metadata={"post_id": post_id}
            )
        
        return {
            "post_id": post_id,
            "saved": post_id in cls._saved_posts[user_id],
            "message": message
        }

    @classmethod
    async def get_saved_posts(cls, user_id: str) -> List[Dict[str, Any]]:
        """Get user's saved posts"""
        saved_ids = cls._saved_posts.get(user_id, set())
        posts = [cls._posts[pid] for pid in saved_ids if pid in cls._posts]
        posts.sort(key=lambda x: x.created_at, reverse=True)
        
        return [cls._format_post(p) for p in posts]

    @classmethod
    async def follow_user(cls, user_id: str, target_user_id: str) -> Dict[str, str]:
        """Follow another user"""
        if user_id == target_user_id:
            raise ValueError("Cannot follow yourself")
        
        # Ensure both users exist
        await cls._get_or_create_user(user_id)
        await cls._get_or_create_user(target_user_id)
        
        if target_user_id in cls._following[user_id]:
            cls._following[user_id].remove(target_user_id)
            cls._followers[target_user_id].remove(user_id)
            message = f"Unfollowed user"
        else:
            cls._following[user_id].add(target_user_id)
            cls._followers[target_user_id].add(user_id)
            message = f"Now following user"
            
            # Award points for following
            streak_service = StreakService()
            await streak_service.log_activity(
                user_id=user_id,
                activity_type="community_share",
                description="Followed a community member",
                metadata={"target_user": target_user_id}
            )
        
        # Update follower counts
        if user_id in cls._users:
            cls._users[user_id]["following_count"] = len(cls._following[user_id])
        if target_user_id in cls._users:
            cls._users[target_user_id]["followers_count"] = len(cls._followers[target_user_id])
        
        return {
            "user_id": user_id,
            "target_user_id": target_user_id,
            "following": target_user_id in cls._following[user_id],
            "message": message
        }

    @classmethod
    async def get_trending(cls) -> Dict[str, Any]:
        """Get trending topics and posts"""
        # Update trending cache if needed
        if not cls._last_trending_update or \
           datetime.now() - cls._last_trending_update > timedelta(hours=1):
            await cls._update_trending()
        
        # Get trending posts (most reactions in last 24h)
        one_day_ago = datetime.now() - timedelta(days=1)
        trending_posts = [
            p for p in cls._posts.values()
            if p.created_at > one_day_ago
        ]
        trending_posts.sort(
            key=lambda x: sum(x.reactions.values()) + x.comment_count + x.share_count,
            reverse=True
        )
        
        return {
            "topics": list(cls._trending_cache.values()),
            "posts": [cls._format_post(p) for p in trending_posts[:10]],
            "updated_at": cls._last_trending_update.isoformat() if cls._last_trending_update else None
        }

    @classmethod
    async def search_posts(cls, query: str, post_type: Optional[PostType] = None) -> List[Dict[str, Any]]:
        """Search posts by keyword"""
        results = []
        query_lower = query.lower()
        
        for post in cls._posts.values():
            # Check title and content
            if query_lower in post.title.lower() or query_lower in post.content.lower():
                results.append(post)
            # Check tags
            elif any(query_lower in tag.lower() for tag in post.tags):
                results.append(post)
            # Check mentioned ingredients
            elif any(query_lower in ing.lower() for ing in post.mentioned_ingredients):
                results.append(post)
        
        # Filter by type if specified
        if post_type:
            results = [p for p in results if p.post_type == post_type]
        
        # Sort by relevance (recent + engagement)
        results.sort(
            key=lambda x: (x.created_at, sum(x.reactions.values())),
            reverse=True
        )
        
        return [cls._format_post(p) for p in results[:20]]

    @classmethod
    async def report_post(cls, post_id: str, user_id: str, reason: str, details: Optional[str] = None) -> Dict[str, str]:
        """Report a post for moderation"""
        if post_id not in cls._posts:
            raise ValueError("Post not found")
        
        report = ReportPost(
            post_id=post_id,
            user_id=user_id,
            reason=reason,
            details=details,
            created_at=datetime.now()
        )
        
        cls._reports.append(report)
        
        # Auto-hide post if multiple reports
        report_count = len([r for r in cls._reports if r.post_id == post_id])
        if report_count >= 3:
            cls._posts[post_id].is_hidden = True
            message = "Post has been hidden due to multiple reports"
        else:
            message = "Report submitted successfully"
        
        return {
            "post_id": post_id,
            "report_id": str(len(cls._reports)),
            "message": message
        }

    @classmethod
    async def delete_post(cls, post_id: str, user_id: str) -> Dict[str, str]:
        """Delete a post (only by author or moderator)"""
        if post_id not in cls._posts:
            raise ValueError("Post not found")
        
        post = cls._posts[post_id]
        
        # Check if user is author or moderator
        user = await cls._get_or_create_user(user_id)
        if post.user_id != user_id and not user.get("is_moderator"):
            raise ValueError("Not authorized to delete this post")
        
        # Delete post and associated comments
        del cls._posts[post_id]
        cls._comments = {k: v for k, v in cls._comments.items() if v.post_id != post_id}
        
        return {
            "post_id": post_id,
            "message": "Post deleted successfully"
        }

    @classmethod
    async def _get_or_create_user(cls, user_id: str) -> Dict[str, Any]:
        """Get or create a community user profile"""
        if user_id in cls._users:
            # Update last active
            cls._users[user_id]["last_active"] = datetime.now()
            return cls._users[user_id]
        
        # Get from user profile service if available
        try:
            profile = UserProfileService.get_user_profile(user_id)
        except:
            profile = {}
        
        # Create new community user
        user = CommunityUser(
            user_id=user_id,
            display_name=profile.get("name", f"User_{user_id[:4]}"),
            bio=profile.get("bio", "Skincare enthusiast on a journey! 🌟"),
            avatar=random.choice(cls.AVATARS),
            badge=random.choice(cls.BADGES),
            skin_type=profile.get("skinType"),
            skin_concerns=profile.get("skinConcerns", []),
            joined_at=datetime.now(),
            last_active=datetime.now()
        )
        
        cls._users[user_id] = user.dict()
        return cls._users[user_id]

    @classmethod
    def _format_post(cls, post: Post) -> Dict[str, Any]:
        """Format post for API response"""
        return {
            "post_id": post.post_id,
            "user": {
                "user_id": "" if post.is_anonymous else post.user_id,
                "name": "Anonymous" if post.is_anonymous else post.user_name,
                "avatar": None if post.is_anonymous else post.user_avatar,
                "badge": None if post.is_anonymous else post.user_badge,
            },
            "post_type": post.post_type.value,
            "title": post.title,
            "content": post.content,
            "images": post.images,
            "tags": post.tags,
            "mentioned_ingredients": post.mentioned_ingredients,
            "mentioned_products": post.mentioned_products,
            "reactions": {k.value: v for k, v in post.reactions.items()},
            "comment_count": post.comment_count,
            "share_count": post.share_count,
            "save_count": post.save_count,
            "view_count": post.view_count,
            "created_at": post.created_at.isoformat(),
            "time_ago": cls._time_ago(post.created_at),
            "is_pinned": post.is_pinned,
        }

    @classmethod
    def _format_comment(cls, comment: Comment) -> Dict[str, Any]:
        """Format comment for API response"""
        return {
            "comment_id": comment.comment_id,
            "user": {
                "user_id": comment.user_id,
                "name": comment.user_name,
                "avatar": comment.user_avatar,
                "badge": comment.user_badge,
            },
            "content": comment.content,
            "images": comment.images,
            "reactions": {k.value: v for k, v in comment.reactions.items()},
            "reply_count": comment.reply_count,
            "replies": [],  # Will be filled by caller
            "created_at": comment.created_at.isoformat(),
            "time_ago": cls._time_ago(comment.created_at),
            "is_edited": comment.is_edited,
        }

    @classmethod
    def _time_ago(cls, dt: datetime) -> str:
        """Convert datetime to "time ago" string"""
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 365:
            return f"{diff.days // 365}y ago"
        if diff.days > 30:
            return f"{diff.days // 30}mo ago"
        if diff.days > 0:
            return f"{diff.d}d ago"
        if diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        if diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        return "just now"

    @classmethod
    async def _update_trending(cls):
        """Update trending topics cache"""
        # Count ingredient mentions in last 24h
        one_day_ago = datetime.now() - timedelta(days=1)
        ingredient_counts = defaultdict(int)
        topic_posts = defaultdict(list)
        
        for post in cls._posts.values():
            if post.created_at > one_day_ago:
                for ing in post.mentioned_ingredients:
                    ingredient_counts[ing] += 1
                    topic_posts[ing].append(post)
        
        # Calculate trend scores
        trending = []
        for ingredient, count in ingredient_counts.items():
            if count >= 3:  # Minimum mentions to trend
                posts = topic_posts[ingredient]
                engagement = sum(
                    sum(p.reactions.values()) + p.comment_count + p.share_count
                    for p in posts
                )
                
                trend_score = (count * 10) + (engagement * 0.5)
                
                trending.append(TrendingTopic(
                    topic=f"#{ingredient}",
                    post_count=count,
                    trend_score=trend_score,
                    last_hour_posts=sum(1 for p in posts if p.created_at > datetime.now() - timedelta(hours=1)),
                    related_ingredients=[ingredient]
                ))
        
        # Sort by trend score
        trending.sort(key=lambda x: x.trend_score, reverse=True)
        
        cls._trending_cache = {t.topic: t.dict() for t in trending[:10]}
        cls._last_trending_update = datetime.now()

    @classmethod
    def _update_trending_for_ingredients(cls, ingredients: List[str]):
        """Update trending when new post mentions ingredients"""
        # This will trigger cache refresh on next request
        cls._last_trending_update = None

    @classmethod
    async def get_user_profile(cls, target_user_id: str, viewer_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a user's community profile"""
        user = await cls._get_or_create_user(target_user_id)
        
        # Get user's posts
        user_posts = [
            cls._format_post(p) for p in cls._posts.values()
            if p.user_id == target_user_id and not p.is_hidden
        ]
        user_posts.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Check if viewer is following
        is_following = False
        if viewer_id:
            is_following = target_user_id in cls._following.get(viewer_id, set())
        
        return {
            **user,
            "posts": user_posts[:10],
            "post_count": len(user_posts),
            "is_following": is_following,
            "followers": list(cls._followers.get(target_user_id, set()))[:10],
            "following": list(cls._following.get(target_user_id, set()))[:10],
        }

    @classmethod
    async def get_user_feed(cls, user_id: str) -> List[Dict[str, Any]]:
        """Get personalized feed for user (posts from followed users)"""
        following = cls._following.get(user_id, set())
        
        feed_posts = []
        for post in cls._posts.values():
            if post.user_id in following and not post.is_hidden:
                feed_posts.append(cls._format_post(post))
        
        feed_posts.sort(key=lambda x: x["created_at"], reverse=True)
        return feed_posts[:30]