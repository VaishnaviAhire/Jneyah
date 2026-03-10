import random
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from ingredients.ingredient_service import IngredientService
from ingredients.ingredient_models import IngredientResponse
import logging

logger = logging.getLogger(__name__)

class IngredientOfDayService:
    
    # In-memory storage for daily ingredient (replace with database in production)
    _daily_ingredient = None
    _last_updated = None
    _user_interactions = {}  # Track user interactions with ingredients
    
    # Fun facts and jokes database (can be extended)
    FUN_FACTS = {
        "retinol": [
            "Retinol was discovered in 1931 by a scientist who probably had amazing skin!",
            "It's part of the retinoid family - the Kardashians of skincare!",
            "Retinol is basically a vampire - hates sunlight and comes alive at night!",
            "Your skin might throw a tantrum for 4-6 weeks before loving retinol. Hang in there!"
        ],
        "vitamin c": [
            "Vitamin C is like that friend who's always positive in the morning (annoying but good for you)!",
            "L-ascorbic acid sounds like a Harry Potter spell, but it's just fancy Vitamin C!",
            "It oxidizes faster than milk left out overnight - keep it in the dark!",
            "Vitamin C brightens skin so much, you'll need sunglasses indoors!"
        ],
        "hyaluronic acid": [
            "Can hold 1000x its weight in water - the camel of skincare!",
            "Found naturally in your body, but decreases with age. Thanks, gravity!",
            "Works best on damp skin. Dry skin + HA = sad panda!",
            "Comes in different molecular sizes - it's not one-size-fits-all!"
        ],
        "niacinamide": [
            "The Switzerland of skincare - neutral and friends with everyone!",
            "Also known as Vitamin B3 - sounds boring but it's the office MVP!",
            "Controls oil better than those blotting papers from high school!",
            "Reduces redness so well, your face will forget how to blush!"
        ],
        "paraben": [
            "The villain of skincare? Maybe not as evil as TikTok makes it seem!",
            "Been around since the 1920s - the grandpa of preservatives!",
            "Prevents mold better than your fridge. Respect the preservation game!",
            "Europe restricts it, USA allows it - skincare has immigration policies too!"
        ],
        "salicylic acid": [
            "The pore plumber - unclogs better than Drano!",
            "Related to aspirin - so it calms inflammation while it works!",
            "Oil-soluble - it can penetrate deeper than your emotional baggage!",
            "Found in willow bark - ancient Egyptians used it. Cleopatra was onto something!"
        ],
        "glycolic acid": [
            "The overachiever of AHAs - smallest molecule, biggest drama!",
            "Discovered from sugar cane - sweet indeed!",
            "Exfoliates so hard, your dead skin cells file a restraining order!",
            "Makes you sun-sensitive - wear SPF or become a tomato!"
        ]
    }
    
    JOKES = {
        "retinol": {
            "setup": "Why did Retinol break up with Sunscreen?",
            "punchline": "Because it needed some space! (Get it? SPF? Space? No? Okay, we tried...) 🌞🚀"
        },
        "vitamin c": {
            "setup": "Why did Vitamin C break up with sunlight?",
            "punchline": "Because it needed a stable relationship! (Oxidation jokes? Anyone?) 🌞💔"
        },
        "hyaluronic acid": {
            "setup": "What did Hyaluronic Acid say to the dry skin?",
            "punchline": "'Quit being so thirsty, I got you!' 💧😎"
        },
        "niacinamide": {
            "setup": "Why did Niacinamide get invited to every party?",
            "punchline": "Because it gets along with EVERYONE! No drama, just results. 🎉"
        },
        "paraben": {
            "setup": "Why did Paraben get a bad reputation?",
            "punchline": "Bad press! It's been preserving products since 1920 - that's a long career! 📰"
        },
        "salicylic acid": {
            "setup": "Why is Salicylic Acid good at its job?",
            "punchline": "It's oil-soluble - it can go deeper than your conversations with your therapist! 🕳️"
        },
        "glycolic acid": {
            "setup": "Why is Glycolic Acid so extra?",
            "punchline": "It's the smallest AHA with the biggest attitude - napoleon complex! 👑"
        }
    }
    
    CELEBRITY_MATCHES = {
        "retinol": {
            "name": "Ross Geller",
            "reason": "'WE WERE ON A BREAK!' - Dramatic, effective, takes three seasons to see results."
        },
        "vitamin c": {
            "name": "Cher",
            "reason": "Timeless, bright, been around forever but still relevant, and definitely has some secrets."
        },
        "hyaluronic acid": {
            "name": "Elle Woods",
            "reason": "Bend and snap! Works hard, stays hydrated, and always looks fabulous."
        },
        "niacinamide": {
            "name": "Keanu Reeves",
            "reason": "Wholesome, good for everyone, secretly powerful, and makes everything better."
        },
        "paraben": {
            "name": "Your Grandparent",
            "reason": "Old school, been around forever, not as bad as everyone says, just doing its job."
        },
        "salicylic acid": {
            "name": "Gordon Ramsay",
            "reason": "Gets in there, cleans things up, might yell a bit, but gets results!"
        },
        "glycolic acid": {
            "name": "Ariana Grande",
            "reason": "Thank u, next (to your dead skin cells)! Powerful, effective, dramatic exit."
        }
    }

    @classmethod
    def get_daily_ingredient(cls) -> Dict[str, Any]:
        """Get the ingredient of the day (changes daily)"""
        today = date.today().isoformat()
        
        # Check if we need to update the daily ingredient
        if cls._last_updated != today or not cls._daily_ingredient:
            cls._update_daily_ingredient()
        
        return cls._daily_ingredient
    
    @classmethod
    def _update_daily_ingredient(cls):
        """Update the daily ingredient (random selection)"""
        # Get all ingredients from service
        all_ingredients = IngredientService.load_dataset()
        
        if not all_ingredients:
            # Fallback to hardcoded list if service fails
            all_ingredients = [
                {"name": "Retinol", "risk_level": "Medium", "risk_score": 55},
                {"name": "Vitamin C", "risk_level": "Low", "risk_score": 15},
                {"name": "Hyaluronic Acid", "risk_level": "Low", "risk_score": 5},
                {"name": "Niacinamide", "risk_level": "Low", "risk_score": 10},
                {"name": "Paraben", "risk_level": "High", "risk_score": 85},
                {"name": "Salicylic Acid", "risk_level": "Medium", "risk_score": 50},
                {"name": "Glycolic Acid", "risk_level": "Medium", "risk_score": 45}
            ]
        
        # Select random ingredient
        selected = random.choice(all_ingredients)
        name_lower = selected["name"].lower()
        
        # Get full ingredient details
        ingredient_data = IngredientService.analyze_ingredient(selected["name"])
        
        # Build daily ingredient with fun content
        cls._daily_ingredient = {
            "date": date.today().isoformat(),
            "name": selected["name"],
            "scientific_name": getattr(ingredient_data, 'scientific_name', None),
            "description": getattr(ingredient_data, 'description', ''),
            "risk_level": selected["risk_level"],
            "risk_score": selected["risk_score"],
            "benefits": getattr(ingredient_data, 'benefits', []),
            "side_effects": getattr(ingredient_data, 'side_effects', []),
            "category": getattr(ingredient_data, 'category', 'unknown'),
            
            # Fun content
            "fun_facts": cls.FUN_FACTS.get(name_lower, [
                f"This ingredient is so mysterious, even we don't know its secrets! 🤔",
                f"Scientists are still studying this one. You're ahead of the curve!"
            ]),
            "joke": cls.JOKES.get(name_lower, {
                "setup": f"Why did the {selected['name']} go to therapy?",
                "punchline": "Because it had too many chemical reactions! 🧪"
            }),
            "celebrity_match": cls.CELEBRITY_MATCHES.get(name_lower, {
                "name": "Mystery Celebrity",
                "reason": "This ingredient is an enigma, wrapped in a riddle, inside a skincare bottle!"
            }),
            "did_you_know": random.choice([
                f"Only 30% of people know what {selected['name']} actually does! You're in the cool club now!",
                f"{selected['name']} has been used in skincare since ancient times. Cleopatra probably used it!",
                f"There are over 100 studies about {selected['name']}. Scientists really like this one!",
                f"You're now 1% smarter just by learning about {selected['name']} today!"
            ]),
            
            # Stats
            "likes": cls._get_ingredient_likes(selected["name"]),
            "views_today": cls._get_ingredient_views(selected["name"]),
            "saved_count": cls._get_ingredient_saves(selected["name"])
        }
        
        cls._last_updated = date.today().isoformat()
        logger.info(f"Daily ingredient updated: {selected['name']}")
    
    @classmethod
    def _get_ingredient_likes(cls, ingredient_name: str) -> int:
        """Get total likes for an ingredient"""
        # In production, query database
        # For now, return random number for demo
        return random.randint(50, 500)
    
    @classmethod
    def _get_ingredient_views(cls, ingredient_name: str) -> int:
        """Get today's views for an ingredient"""
        # In production, query database
        return random.randint(100, 1000)
    
    @classmethod
    def _get_ingredient_saves(cls, ingredient_name: str) -> int:
        """Get number of times ingredient was saved"""
        return random.randint(10, 200)
    
    @classmethod
    def record_interaction(cls, user_id: str, ingredient_name: str, action: str):
        """Record user interaction with ingredient"""
        key = f"{ingredient_name}_{date.today().isoformat()}"
        
        if key not in cls._user_interactions:
            cls._user_interactions[key] = {
                "ingredient": ingredient_name,
                "date": date.today().isoformat(),
                "likes": 0,
                "shares": 0,
                "views": 0,
                "saves": 0,
                "users": set()
            }
        
        interaction = cls._user_interactions[key]
        interaction["users"].add(user_id)
        
        if action == "like":
            interaction["likes"] += 1
        elif action == "share":
            interaction["shares"] += 1
        elif action == "view":
            interaction["views"] += 1
        elif action == "save":
            interaction["saves"] += 1
    
    @classmethod
    def get_ingredient_stats(cls, ingredient_name: str) -> Dict[str, Any]:
        """Get statistics for an ingredient"""
        stats = {
            "total_likes": 0,
            "total_views": 0,
            "total_saves": 0,
            "daily_breakdown": {}
        }
        
        for key, data in cls._user_interactions.items():
            if data["ingredient"].lower() == ingredient_name.lower():
                stats["total_likes"] += data["likes"]
                stats["total_views"] += data["views"]
                stats["total_saves"] += data["saves"]
                stats["daily_breakdown"][data["date"]] = {
                    "likes": data["likes"],
                    "views": data["views"],
                    "unique_users": len(data["users"])
                }
        
        return stats

    @classmethod
    def get_ingredient_by_name(cls, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific ingredient by name"""
        ingredient_data = IngredientService.analyze_ingredient(name)
        
        if not ingredient_data or ingredient_data.risk_level == "Unknown":
            return None
        
        name_lower = name.lower()
        
        return {
            "name": ingredient_data.name,
            "scientific_name": getattr(ingredient_data, 'scientific_name', None),
            "description": ingredient_data.description,
            "risk_level": ingredient_data.risk_level,
            "risk_score": ingredient_data.risk_score,
            "benefits": ingredient_data.benefits,
            "side_effects": ingredient_data.side_effects,
            "category": getattr(ingredient_data, 'category', 'unknown'),
            "fun_facts": cls.FUN_FACTS.get(name_lower, [
                f"This ingredient is still being studied. You're a pioneer!"
            ]),
            "joke": cls.JOKES.get(name_lower, {
                "setup": f"What do you call a {name} that tells jokes?",
                "punchline": "A funny-ment! (We'll work on our jokes...) 😅"
            }),
            "celebrity_match": cls.CELEBRITY_MATCHES.get(name_lower, {
                "name": "Undercover Celebrity",
                "reason": "This ingredient works behind the scenes, like a stunt double for your skin!"
            }),
            "did_you_know": f"{name} is one of the most researched ingredients in skincare. Science! 🔬"
        }