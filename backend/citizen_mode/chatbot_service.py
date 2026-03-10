import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from difflib import get_close_matches

from ingredients.ingredient_service import IngredientService
from user.user_profile_service import UserProfileService
from interaction_engine.interaction_service import InteractionService
from safety_engine.risk_scoring import RiskScoringService

logger = logging.getLogger(__name__)

class ChatbotService:
    
    # Intent patterns
    INTENT_PATTERNS = {
        "greeting": [
            r"hi|hello|hey|greetings|good morning|good afternoon|good evening",
            r"howdy|what's up|sup|yo"
        ],
        "ingredient_info": [
            r"tell me about (.*)",
            r"what is (.*)",
            r"information on (.*)",
            r"details? about (.*)",
            r"explain (.*)",
            r"what does (.*) do",
            r"is (.*) safe",
            r"how safe is (.*)",
            r"(.*) benefits",
            r"(.*) side effects"
        ],
        "product_analysis": [
            r"analyze (.*) product",
            r"check (.*) ingredients?",
            r"is this product safe",
            r"review (.*)",
            r"what do you think of (.*)"
        ],
        "comparison": [
            r"compare (.*) and (.*)",
            r"which is better (.*) or (.*)",
            r"difference between (.*) and (.*)",
            r"(.*) vs (.*)"
        ],
        "recommendation": [
            r"recommend (.*) for (.*)",
            r"suggest (.*) for (.*)",
            r"what should I use for (.*)",
            r"best (.*) for (.*)",
            r"alternatives? to (.*)"
        ],
        "interaction": [
            r"can I use (.*) with (.*)",
            r"is it safe to combine (.*) and (.*)",
            r"do (.*) and (.*) work together",
            r"(.*) interaction with (.*)"
        ],
        "skin_concern": [
            r"what's good for (.*)",
            r"how to treat (.*)",
            r"help with (.*)",
            r"remedy for (.*)",
            r"solution for (.*)"
        ],
        "profile_advice": [
            r"for my skin",
            r"for me",
            r"based on my profile",
            r"personalized advice",
            r"recommendations? for me"
        ],
        "help": [
            r"help",
            r"what can you do",
            r"how to use",
            r"capabilities",
            r"features"
        ],
        "farewell": [
            r"bye|goodbye|see you|thanks|thank you"
        ]
    }

    # Common skin concerns mapping
    SKIN_CONCERNS_MAP = {
        "acne": ["acne", "pimples", "breakouts", "zits", "spots"],
        "aging": ["aging", "wrinkles", "fine lines", "old", "anti-aging"],
        "dryness": ["dry", "dryness", "flaky", "dehydrated", "tight"],
        "oiliness": ["oily", "oil", "shine", "greasy", "sebum"],
        "dark_spots": ["dark spots", "hyperpigmentation", "melasma", "discoloration", "uneven tone"],
        "redness": ["redness", "irritation", "inflammation", "sensitive", "rosacea"],
        "large_pores": ["large pores", "pores", "open pores"],
        "sensitivity": ["sensitive", "reactive", "stinging", "burning"]
    }

    # Common ingredient categories
    INGREDIENT_CATEGORIES = {
        "moisturizer": ["glycerin", "hyaluronic acid", "ceramide", "squalane", "shea butter"],
        "treatment": ["retinol", "vitamin c", "niacinamide", "salicylic acid", "benzoyl peroxide"],
        "cleanser": ["sodium lauryl sulfate", "cocamidopropyl betaine", "salicylic acid"],
        "sunscreen": ["zinc oxide", "titanium dioxide", "avobenzone", "octinoxate"]
    }

    def __init__(self):
        self.conversation_history = []
        self.user_context = {}

    async def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Process user message and return response
        """
        # Store message in history
        self.conversation_history.append({
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "direction": "user"
        })

        # Detect intent
        intent = self._detect_intent(message)
        
        # Get user profile if available
        user_profile = None
        if user_id:
            try:
                user_profile = UserProfileService.get_user_profile(user_id)
            except:
                pass

        # Generate response based on intent
        response = await self._generate_response(intent, message, user_profile, user_id)

        # Store response in history
        self.conversation_history.append({
            "user_id": user_id,
            "message": response["text"],
            "timestamp": datetime.now().isoformat(),
            "direction": "bot",
            "intent": intent,
            "suggestions": response.get("suggestions", [])
        })

        return response

    def _detect_intent(self, message: str) -> str:
        """
        Detect user intent from message
        """
        message_lower = message.lower()
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return intent
        
        return "unknown"

    async def _generate_response(self, intent: str, message: str, user_profile: Optional[Dict], user_id: str) -> Dict[str, Any]:
        """
        Generate appropriate response based on intent
        """
        response = {
            "text": "",
            "suggestions": [],
            "data": None,
            "type": "text"
        }

        if intent == "greeting":
            response["text"] = self._get_greeting_response(user_profile)
            response["suggestions"] = [
                "Tell me about Vitamin C",
                "What's good for acne?",
                "Is retinol safe?",
                "Help me find a moisturizer"
            ]

        elif intent == "ingredient_info":
            response = await self._handle_ingredient_info(message, user_profile)

        elif intent == "product_analysis":
            response = await self._handle_product_analysis(message, user_profile)

        elif intent == "comparison":
            response = await self._handle_comparison(message, user_profile)

        elif intent == "recommendation":
            response = await self._handle_recommendation(message, user_profile)

        elif intent == "interaction":
            response = await self._handle_interaction(message, user_profile)

        elif intent == "skin_concern":
            response = await self._handle_skin_concern(message, user_profile)

        elif intent == "profile_advice":
            response = await self._handle_profile_advice(user_profile)

        elif intent == "help":
            response = self._get_help_response()

        elif intent == "farewell":
            response["text"] = "You're welcome! Feel free to ask if you have more questions about ingredients or skincare. Have a great day! 🌟"
            response["suggestions"] = ["Tell me about retinol", "What's new today?"]

        else:
            response = await self._handle_unknown(message)

        return response

    def _get_greeting_response(self, user_profile: Optional[Dict]) -> str:
        """Get personalized greeting"""
        if user_profile:
            name = user_profile.get("name", "there")
            skin_type = user_profile.get("skinType", "")
            
            if skin_type:
                return f"Hi {name}! 👋 I see you have {skin_type} skin. How can I help you with your skincare questions today?"
            else:
                return f"Hi {name}! 👋 I'm your ingredient safety assistant. Ask me about any ingredient, product, or skincare concern!"
        else:
            return "Hello! 👋 I'm your ingredient safety assistant. You can ask me about ingredients, product safety, or get personalized recommendations. What would you like to know?"

    async def _handle_ingredient_info(self, message: str, user_profile: Optional[Dict]) -> Dict[str, Any]:
        """Handle ingredient information queries"""
        # Extract ingredient name
        ingredient = self._extract_ingredient_from_message(message)
        
        if not ingredient:
            return {
                "text": "I couldn't identify which ingredient you're asking about. Could you please specify the ingredient name? For example: 'Tell me about retinol'",
                "suggestions": ["Tell me about Vitamin C", "What is hyaluronic acid?", "Is niacinamide safe?"],
                "type": "text"
            }

        # Get ingredient data
        ingredient_data = IngredientService.analyze_ingredient(ingredient)
        
        if not ingredient_data or ingredient_data.risk_level == "Unknown":
            return {
                "text": f"I don't have enough information about '{ingredient}' in my database. Could you try another ingredient?",
                "suggestions": ["Tell me about retinol", "What is niacinamide?", "Explain hyaluronic acid"],
                "type": "text"
            }

        # Personalize if user profile available
        personalized_risk = None
        if user_profile:
            personalized_risk = RiskScoringService.calculate_personalized_risk(
                ingredient_data, user_profile
            )

        # Build response
        response_text = f"**{ingredient_data.name}**\n\n"
        response_text += f"{ingredient_data.description}\n\n"
        
        response_text += f"**Risk Level:** {ingredient_data.risk_level} (Score: {ingredient_data.risk_score}/100)\n\n"
        
        if ingredient_data.benefits:
            response_text += "**✅ Benefits:**\n"
            for benefit in ingredient_data.benefits[:3]:
                response_text += f"• {benefit}\n"
            response_text += "\n"
        
        if ingredient_data.side_effects:
            response_text += "**⚠️ Side Effects:**\n"
            for effect in ingredient_data.side_effects[:3]:
                response_text += f"• {effect}\n"
            response_text += "\n"

        if personalized_risk and personalized_risk.get("warnings"):
            response_text += "**🔔 For Your Profile:**\n"
            for warning in personalized_risk["warnings"][:2]:
                response_text += f"• {warning}\n"
            response_text += "\n"

        if ingredient_data.alternatives:
            response_text += "**🔄 Safer Alternatives:**\n"
            response_text += f"Consider: {', '.join(ingredient_data.alternatives[:3])}\n"

        suggestions = [
            f"What are alternatives to {ingredient_data.name}?",
            f"Can I use {ingredient_data.name} with Vitamin C?",
            f"Best products with {ingredient_data.name}"
        ]

        return {
            "text": response_text,
            "suggestions": suggestions,
            "data": ingredient_data.dict(),
            "type": "ingredient"
        }

    async def _handle_product_analysis(self, message: str, user_profile: Optional[Dict]) -> Dict[str, Any]:
        """Handle product analysis queries"""
        # Extract product name or ingredients
        product_query = self._extract_product_from_message(message)
        
        if not product_query:
            return {
                "text": "I'd be happy to analyze a product for you! Could you tell me the product name or list its ingredients?",
                "suggestions": ["Check moisturizer ingredients", "Is sunscreen safe?", "Analyze retinol cream"],
                "type": "text"
            }

        # For now, provide general advice
        response_text = f"To properly analyze '{product_query}', I would need to see its full ingredient list.\n\n"
        response_text += "**What to look for:**\n"
        response_text += "• Check the ingredient list order (first ingredients are highest concentration)\n"
        response_text += "• Look for active ingredients like retinol, vitamin C, or niacinamide\n"
        response_text += "• Be cautious of fragrances if you have sensitive skin\n"
        response_text += "• Avoid known irritants like denatured alcohol high on the list\n\n"
        
        if user_profile:
            response_text += "Based on your profile, you should pay special attention to avoiding ingredients you're allergic to."

        return {
            "text": response_text,
            "suggestions": ["How to read ingredient labels?", "What are active ingredients?", "Common irritants to avoid"],
            "type": "text"
        }

    async def _handle_comparison(self, message: str, user_profile: Optional[Dict]) -> Dict[str, Any]:
        """Handle ingredient comparison queries"""
        # Extract two ingredients
        ingredients = self._extract_two_ingredients(message)
        
        if len(ingredients) < 2:
            return {
                "text": "I'd be happy to compare ingredients! Please specify two ingredients. For example: 'Compare retinol and vitamin C'",
                "suggestions": ["Retinol vs Vitamin C", "Hyaluronic acid vs glycerin", "Niacinamide vs vitamin C"],
                "type": "text"
            }

        ing1_data = IngredientService.analyze_ingredient(ingredients[0])
        ing2_data = IngredientService.analyze_ingredient(ingredients[1])

        if ing1_data.risk_level == "Unknown" or ing2_data.risk_level == "Unknown":
            return {
                "text": f"I couldn't find complete information for one of these ingredients. Please check the names and try again.",
                "suggestions": ["Compare retinol and vitamin C", "Hyaluronic acid vs glycerin"],
                "type": "text"
            }

        # Build comparison
        response_text = f"**Comparing {ing1_data.name} vs {ing2_data.name}**\n\n"

        response_text += f"**{ing1_data.name}**\n"
        response_text += f"• Risk: {ing1_data.risk_level} ({ing1_data.risk_score}/100)\n"
        response_text += f"• Best for: {', '.join(ing1_data.benefits[:2])}\n"
        response_text += f"• Watch out: {', '.join(ing1_data.side_effects[:2])}\n\n"

        response_text += f"**{ing2_data.name}**\n"
        response_text += f"• Risk: {ing2_data.risk_level} ({ing2_data.risk_score}/100)\n"
        response_text += f"• Best for: {', '.join(ing2_data.benefits[:2])}\n"
        response_text += f"• Watch out: {', '.join(ing2_data.side_effects[:2])}\n\n"

        # Check interaction
        interaction = InteractionService.check_interaction(ingredients[0], ingredients[1])
        if interaction:
            response_text += f"**Interaction:** {interaction['warning']}\n\n"

        # Recommendation
        if ing1_data.risk_score < ing2_data.risk_score:
            response_text += f"**Verdict:** {ing1_data.name} has a lower risk profile, but both can be effective for different concerns."
        else:
            response_text += f"**Verdict:** {ing2_data.name} has a lower risk profile, but both can be effective for different concerns."

        return {
            "text": response_text,
            "suggestions": ["Can I use both together?", "Which is better for anti-aging?", "Any side effects?"],
            "data": {"ingredient1": ing1_data.dict(), "ingredient2": ing2_data.dict()},
            "type": "comparison"
        }

    async def _handle_recommendation(self, message: str, user_profile: Optional[Dict]) -> Dict[str, Any]:
        """Handle recommendation queries"""
        # Extract concern or need
        concern = self._extract_concern_from_message(message)
        
        if not concern:
            return {
                "text": "I can help recommend ingredients for your concerns! What are you looking to address? (e.g., acne, aging, dryness)",
                "suggestions": ["Ingredients for acne", "Best for aging skin", "Help with dryness"],
                "type": "text"
            }

        # Map concern to ingredients
        recommendations = self._get_recommendations_for_concern(concern, user_profile)

        response_text = f"**For {concern}**, here are some ingredients to look for:\n\n"
        
        for rec in recommendations:
            response_text += f"• **{rec['name']}** - {rec['reason']}\n"
            if rec.get('caution'):
                response_text += f"  ⚠️ {rec['caution']}\n"

        if user_profile:
            response_text += f"\n**Based on your profile:**\n"
            if user_profile.get("skinType") == "sensitive":
                response_text += "• Start with lower concentrations and patch test\n"
            if "acne" in user_profile.get("skinConcerns", []):
                response_text += "• Look for non-comedogenic products\n"

        suggestions = [
            f"Best products with these ingredients",
            f"How to use {recommendations[0]['name']}",
            f"Side effects of {recommendations[0]['name']}"
        ]

        return {
            "text": response_text,
            "suggestions": suggestions,
            "type": "recommendation"
        }

    async def _handle_interaction(self, message: str, user_profile: Optional[Dict]) -> Dict[str, Any]:
        """Handle ingredient interaction queries"""
        # Extract two ingredients
        ingredients = self._extract_two_ingredients(message)
        
        if len(ingredients) < 2:
            return {
                "text": "I can check if ingredients work well together! Please specify two ingredients. For example: 'Can I use retinol with vitamin C?'",
                "suggestions": ["Retinol with vitamin C", "Niacinamide with vitamin C", "AHAs with BHAs"],
                "type": "text"
            }

        # Check interaction
        interaction = InteractionService.check_interaction(ingredients[0], ingredients[1])

        if interaction:
            response_text = f"**⚠️ Caution: Possible Interaction**\n\n"
            response_text += f"Using **{ingredients[0]}** with **{ingredients[1]}** may cause:\n"
            response_text += f"• {interaction['warning']}\n\n"
            response_text += f"**Recommendation:** {interaction.get('recommendation', 'Use at different times of day')}"
        else:
            response_text = f"✅ **Good news!**\n\n"
            response_text += f"**{ingredients[0]}** and **{ingredients[1]}** are generally safe to use together.\n\n"
            response_text += "However, always:\n"
            response_text += "• Patch test new combinations\n"
            response_text += "• Introduce one product at a time\n"
            response_text += "• Monitor your skin's reaction"

        return {
            "text": response_text,
            "suggestions": ["Best time to use retinol", "How to layer skincare", "Morning vs night routine"],
            "type": "interaction"
        }

    async def _handle_skin_concern(self, message: str, user_profile: Optional[Dict]) -> Dict[str, Any]:
        """Handle skin concern queries"""
        # Extract concern
        concern = self._extract_concern_from_message(message)
        
        if not concern:
            return {
                "text": "I can help with various skin concerns! What would you like help with? (e.g., acne, aging, dark spots)",
                "suggestions": ["Help with acne", "Anti-aging routine", "Reduce dark spots"],
                "type": "text"
            }

        # Get advice for concern
        advice = self._get_skin_concern_advice(concern, user_profile)

        response_text = f"**Tips for {concern}:**\n\n"
        response_text += f"{advice['description']}\n\n"
        
        response_text += "**Recommended ingredients:**\n"
        for ing in advice['ingredients']:
            response_text += f"• {ing}\n"
        
        response_text += "\n**Ingredients to avoid:**\n"
        for ing in advice['avoid']:
            response_text += f"• {ing}\n"

        if user_profile:
            response_text += f"\n**Based on your profile:**\n"
            if user_profile.get("skinType") == "sensitive":
                response_text += "• Be extra gentle and patch test everything\n"
            if concern in user_profile.get("skinConcerns", []):
                response_text += "• You're already targeting this concern - consistency is key!"

        suggestions = [
            f"Products for {concern}",
            f"Routine for {concern}",
            f"How long to see results for {concern}"
        ]

        return {
            "text": response_text,
            "suggestions": suggestions,
            "type": "advice"
        }

    async def _handle_profile_advice(self, user_profile: Optional[Dict]) -> Dict[str, Any]:
        """Handle personalized advice based on user profile"""
        if not user_profile:
            return {
                "text": "I'd love to give you personalized advice! Please complete your profile first so I can understand your skin better.",
                "suggestions": ["Complete my profile", "General skincare tips", "Popular ingredients"],
                "type": "text"
            }

        response_text = "**🎯 Personalized Recommendations**\n\n"
        
        # Skin type advice
        skin_type = user_profile.get("skinType", "normal")
        response_text += f"**For your {skin_type} skin:**\n"
        
        if skin_type == "sensitive":
            response_text += "• Look for fragrance-free, alcohol-free products\n"
            response_text += "• Patch test everything new\n"
            response_text += "• Avoid harsh exfoliants\n"
        elif skin_type == "oily":
            response_text += "• Gel or foam cleansers work well\n"
            response_text += "• Niacinamide helps regulate oil\n"
            response_text += "• Don't skip moisturizer!\n"
        elif skin_type == "dry":
            response_text += "• Creamy, hydrating cleansers\n"
            response_text += "• Look for hyaluronic acid and ceramides\n"
            response_text += "• Avoid high-alcohol products\n"
        
        response_text += "\n"

        # Concern-based advice
        concerns = user_profile.get("skinConcerns", [])
        if concerns:
            response_text += f"**For your {', '.join(concerns)}:**\n"
            for concern in concerns[:2]:
                advice = self._get_skin_concern_advice(concern, user_profile)
                response_text += f"• {concern.title()}: {advice['ingredients'][0]}, {advice['ingredients'][1] if len(advice['ingredients']) > 1 else ''}\n"
            response_text += "\n"

        # Allergy warnings
        allergies = user_profile.get("skincareAllergies", [])
        if allergies:
            response_text += f"**⚠️ Remember to avoid:**\n"
            for allergy in allergies:
                response_text += f"• {allergy}\n"
            response_text += "\n"

        return {
            "text": response_text,
            "suggestions": ["Update my profile", "Product recommendations", "Routine builder"],
            "type": "profile"
        }

    def _get_help_response(self) -> Dict[str, Any]:
        """Get help information"""
        response_text = "**🤖 I can help you with:**\n\n"
        response_text += "• **Ingredient info** - 'Tell me about retinol'\n"
        response_text += "• **Product analysis** - 'Check this moisturizer'\n"
        response_text += "• **Comparisons** - 'Compare vitamin C and niacinamide'\n"
        response_text += "• **Recommendations** - 'What's good for acne?'\n"
        response_text += "• **Interactions** - 'Can I use retinol with vitamin C?'\n"
        response_text += "• **Skin concerns** - 'Help with dark spots'\n"
        response_text += "• **Personalized advice** - 'Recommendations for me'\n\n"
        response_text += "Just ask me anything about skincare ingredients!"

        return {
            "text": response_text,
            "suggestions": ["Tell me about retinol", "What's good for acne?", "Personalized advice"],
            "type": "help"
        }

    async def _handle_unknown(self, message: str) -> Dict[str, Any]:
        """Handle unknown queries"""
        return {
            "text": "I'm not sure I understood that. Could you rephrase or ask me about ingredients, products, or skincare concerns?",
            "suggestions": ["Help", "Tell me about retinol", "What can you do?"],
            "type": "unknown"
        }

    def _extract_ingredient_from_message(self, message: str) -> Optional[str]:
        """Extract ingredient name from message"""
        # Common ingredient patterns
        patterns = [
            r"about\s+([A-Za-z\s-]+?)(?:\?|\.|$)",
            r"what is\s+([A-Za-z\s-]+?)(?:\?|\.|$)",
            r"explain\s+([A-Za-z\s-]+?)(?:\?|\.|$)",
            r"is\s+([A-Za-z\s-]+?)\s+safe",
            r"tell me about\s+([A-Za-z\s-]+?)(?:\?|\.|$)"
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip().lower()

        # If no pattern matches, try to find any common ingredient
        words = message.split()
        for word in words:
            # Check against common ingredients
            common_ingredients = ["retinol", "vitamin c", "niacinamide", "hyaluronic acid", 
                                  "salicylic acid", "glycolic acid", "paraben", "fragrance"]
            for ing in common_ingredients:
                if ing in message.lower():
                    return ing

        return None

    def _extract_two_ingredients(self, message: str) -> List[str]:
        """Extract two ingredients from comparison message"""
        # Pattern for "X and Y" or "X vs Y" or "X with Y"
        patterns = [
            r"(?:compare|between)\s+([A-Za-z\s-]+?)\s+(?:and|vs|with)\s+([A-Za-z\s-]+?)(?:\?|\.|$)",
            r"([A-Za-z\s-]+?)\s+(?:and|vs|with)\s+([A-Za-z\s-]+?)(?:\?|\.|$)"
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return [match.group(1).strip().lower(), match.group(2).strip().lower()]

        return []

    def _extract_product_from_message(self, message: str) -> Optional[str]:
        """Extract product name from message"""
        patterns = [
            r"analyze\s+([A-Za-z\s-]+?)(?:\?|\.|$)",
            r"check\s+([A-Za-z\s-]+?)(?:\?|\.|$)",
            r"review\s+([A-Za-z\s-]+?)(?:\?|\.|$)",
            r"what do you think of\s+([A-Za-z\s-]+?)(?:\?|\.|$)"
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_concern_from_message(self, message: str) -> Optional[str]:
        """Extract skin concern from message"""
        message_lower = message.lower()
        
        for concern, keywords in self.SKIN_CONCERNS_MAP.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return concern

        return None

    def _get_recommendations_for_concern(self, concern: str, user_profile: Optional[Dict]) -> List[Dict]:
        """Get ingredient recommendations for a concern"""
        recommendations = {
            "acne": [
                {"name": "Salicylic Acid", "reason": "Unclogs pores and reduces inflammation", "caution": "Can be drying, start with low concentration"},
                {"name": "Niacinamide", "reason": "Reduces inflammation and regulates oil", "caution": "Generally well-tolerated"},
                {"name": "Benzoyl Peroxide", "reason": "Kills acne-causing bacteria", "caution": "Can bleach fabrics, start with 2.5%"}
            ],
            "aging": [
                {"name": "Retinol", "reason": "Boosts collagen and speeds cell turnover", "caution": "Can cause irritation, start slow"},
                {"name": "Vitamin C", "reason": "Antioxidant that brightens and protects", "caution": "Can oxidize, choose dark packaging"},
                {"name": "Peptides", "reason": "Support collagen production", "caution": "Gentle, good for sensitive skin"}
            ],
            "dryness": [
                {"name": "Hyaluronic Acid", "reason": "Attracts and holds moisture", "caution": "Apply to damp skin"},
                {"name": "Ceramides", "reason": "Restore skin barrier", "caution": "Look in moisturizers"},
                {"name": "Squalane", "reason": "Lightweight, non-comedogenic oil", "caution": "Suitable for most skin types"}
            ],
            "dark_spots": [
                {"name": "Vitamin C", "reason": "Brightens and fades dark spots", "caution": "Use in morning"},
                {"name": "Niacinamide", "reason": "Reduces pigmentation", "caution": "Works well with other ingredients"},
                {"name": "Alpha Arbutin", "reason": "Targeted dark spot treatment", "caution": "Gentle, good for sensitive skin"}
            ]
        }

        return recommendations.get(concern, [
            {"name": "Consult a dermatologist", "reason": "For personalized advice", "caution": ""}
        ])

    def _get_skin_concern_advice(self, concern: str, user_profile: Optional[Dict]) -> Dict:
        """Get detailed advice for skin concern"""
        advice_db = {
            "acne": {
                "description": "Acne occurs when pores become clogged with oil and dead skin cells.",
                "ingredients": ["Salicylic acid", "Benzoyl peroxide", "Niacinamide", "Retinoids"],
                "avoid": ["Coconut oil", "Isopropyl myristate", "Heavy oils", "Fragrance"]
            },
            "aging": {
                "description": "Aging skin shows fine lines, wrinkles, and loss of firmness due to collagen breakdown.",
                "ingredients": ["Retinol", "Vitamin C", "Peptides", "Ceramides", "Sunscreen"],
                "avoid": ["Harsh alcohols", "Irritating fragrances", "Over-exfoliation"]
            },
            "dryness": {
                "description": "Dry skin lacks moisture and natural oils, feeling tight and flaky.",
                "ingredients": ["Hyaluronic acid", "Ceramides", "Squalane", "Shea butter", "Glycerin"],
                "avoid": ["Denatured alcohol", "Sulfates", "Harsh cleansers", "Fragrance"]
            },
            "oiliness": {
                "description": "Oily skin produces excess sebum, leading to shine and potential breakouts.",
                "ingredients": ["Niacinamide", "Salicylic acid", "Clay", "Zinc PCA"],
                "avoid": ["Heavy oils", "Alcohol", "Thick creams"]
            },
            "sensitivity": {
                "description": "Sensitive skin reacts easily to products and environmental factors.",
                "ingredients": ["Centella asiatica", "Ceramides", "Oat", "Panthenol", "Aloe"],
                "avoid": ["Fragrance", "Essential oils", "Alcohol", "Harsh exfoliants"]
            }
        }

        return advice_db.get(concern, {
            "description": "For this concern, it's best to consult with a dermatologist.",
            "ingredients": ["Consult professional"],
            "avoid": ["Harsh ingredients", "Fragrance"]
        })