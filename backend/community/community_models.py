from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PostType(str, Enum):
    PRODUCT_REVIEW = "product_review"
    INGREDIENT_QUESTION = "ingredient_question"
    ROUTINE_SHARE = "routine_share"
    BEFORE_AFTER = "before_after"
    TIP_TRICK = "tip_trick"
    ALERT_WARNING = "alert_warning"
    SUCCESS_STORY = "success_story"
    DILEMMA = "dilemma"
    DETOX_JOURNEY = "detox_journey"
    ECO_CHALLENGE = "eco_challenge"

class ReactionType(str, Enum):
    LIKE = "like"
    LOVE = "love"
    HELPFUL = "helpful"
    LOL = "lol"
    WOW = "wow"
    SAD = "sad"
    ANGRY = "angry"

class Post(BaseModel):
    post_id: str
    user_id: str
    user_name: str
    user_avatar: Optional[str] = None
    user_badge: Optional[str] = None
    
    post_type: PostType
    title: str
    content: str
    images: List[str] = []
    tags: List[str] = []
    mentioned_ingredients: List[str] = []
    mentioned_products: List[str] = []
    
    reactions: Dict[ReactionType, int] = {
        ReactionType.LIKE: 0,
        ReactionType.LOVE: 0,
        ReactionType.HELPFUL: 0,
        ReactionType.LOL: 0,
        ReactionType.WOW: 0,
        ReactionType.SAD: 0,
        ReactionType.ANGRY: 0
    }
    user_reactions: Dict[str, ReactionType] = {}  # user_id -> reaction
    
    comment_count: int = 0
    share_count: int = 0
    save_count: int = 0
    view_count: int = 0
    
    is_anonymous: bool = False
    is_edited: bool = False
    is_pinned: bool = False
    is_hidden: bool = False
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_activity_at: datetime = Field(default_factory=datetime.now)

class Comment(BaseModel):
    comment_id: str
    post_id: str
    user_id: str
    user_name: str
    user_avatar: Optional[str] = None
    user_badge: Optional[str] = None
    
    content: str
    images: List[str] = []
    mentioned_users: List[str] = []
    
    reactions: Dict[ReactionType, int] = {
        ReactionType.LIKE: 0,
        ReactionType.LOVE: 0,
        ReactionType.HELPFUL: 0,
        ReactionType.LOL: 0,
    }
    user_reactions: Dict[str, ReactionType] = {}
    
    reply_to: Optional[str] = None  # comment_id this is replying to
    replies: List[str] = []  # list of reply comment_ids
    reply_count: int = 0
    
    is_edited: bool = False
    is_hidden: bool = False
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CommunityUser(BaseModel):
    user_id: str
    display_name: str
    bio: Optional[str] = None
    avatar: Optional[str] = None
    badge: Optional[str] = None
    
    followers_count: int = 0
    following_count: int = 0
    post_count: int = 0
    comment_count: int = 0
    helpful_count: int = 0
    
    skin_type: Optional[str] = None
    skin_concerns: List[str] = []
    favorite_ingredients: List[str] = []
    
    joined_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)
    
    is_verified: bool = False
    is_expert: bool = False
    is_moderator: bool = False

class CommunityFeed(BaseModel):
    feed_id: str
    user_id: str
    posts: List[str]  # list of post_ids
    last_updated: datetime = Field(default_factory=datetime.now)

class PostCreate(BaseModel):
    post_type: PostType
    title: str
    content: str
    images: List[str] = []
    tags: List[str] = []
    mentioned_ingredients: List[str] = []
    mentioned_products: List[str] = []
    is_anonymous: bool = False

class CommentCreate(BaseModel):
    content: str
    images: List[str] = []
    reply_to: Optional[str] = None

class ReportPost(BaseModel):
    post_id: str
    user_id: str
    reason: str
    details: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class TrendingTopic(BaseModel):
    topic: str
    post_count: int
    trend_score: float
    last_hour_posts: int
    related_ingredients: List[str] = []