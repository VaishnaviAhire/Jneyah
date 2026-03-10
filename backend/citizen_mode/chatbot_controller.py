from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
from datetime import datetime
import json
import asyncio
import logging

from .chatbot_service import ChatbotService
from user.user_profile_service import UserProfileService
from user.user_profile_service import UserProfileService  # This is fine
from interaction_engine.interaction_service import InteractionService  # This is fine
from safety_engine.risk_scoring import RiskScoringService  # This is fine
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chatbot", tags=["chatbot"])

# Store active connections
active_connections = {}
chatbot_instances = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.chat_histories: Dict[str, List] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        if user_id not in self.chat_histories:
            self.chat_histories[user_id] = []
        logger.info(f"User {user_id} connected to chatbot")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected from chatbot")

    async def send_message(self, user_id: str, message: Dict[str, Any]):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    def add_to_history(self, user_id: str, message: Dict[str, Any]):
        if user_id in self.chat_histories:
            self.chat_histories[user_id].append(message)
            # Keep only last 50 messages
            if len(self.chat_histories[user_id]) > 50:
                self.chat_histories[user_id] = self.chat_histories[user_id][-50:]

    def get_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        if user_id in self.chat_histories:
            return self.chat_histories[user_id][-limit:]
        return []

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(user_id, websocket)
    
    # Initialize chatbot for this user
    if user_id not in chatbot_instances:
        chatbot_instances[user_id] = ChatbotService()
    
    chatbot = chatbot_instances[user_id]
    
    try:
        # Send welcome message
        user_profile = UserProfileService.get_user_profile(user_id)
        welcome_response = await chatbot.process_message(user_id, "hello")
        welcome_response["type"] = "welcome"
        await manager.send_message(user_id, welcome_response)
        manager.add_to_history(user_id, {"role": "assistant", "content": welcome_response})

        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Add user message to history
            manager.add_to_history(user_id, {"role": "user", "content": message_data})
            
            # Process message
            response = await chatbot.process_message(
                user_id=user_id,
                message=message_data.get("text", "")
            )
            
            # Add suggestions if not present
            if "suggestions" not in response:
                response["suggestions"] = []
            
            # Send response
            await manager.send_message(user_id, response)
            
            # Add to history
            manager.add_to_history(user_id, {"role": "assistant", "content": response})
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(user_id)

@router.post("/message")
async def send_message(
    user_id: str,
    message: Dict[str, Any]
) -> Dict[str, Any]:
    """HTTP endpoint for sending messages (fallback)"""
    try:
        # Initialize chatbot if needed
        if user_id not in chatbot_instances:
            chatbot_instances[user_id] = ChatbotService()
        
        chatbot = chatbot_instances[user_id]
        
        # Process message
        response = await chatbot.process_message(
            user_id=user_id,
            message=message.get("text", "")
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Message processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 20) -> List[Dict]:
    """Get user's chat history"""
    try:
        history = manager.get_history(user_id, limit)
        return history
    except Exception as e:
        logger.error(f"History fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history/{user_id}")
async def clear_chat_history(user_id: str) -> Dict[str, str]:
    """Clear user's chat history"""
    try:
        if user_id in manager.chat_histories:
            manager.chat_histories[user_id] = []
        return {"status": "success", "message": "Chat history cleared"}
    except Exception as e:
        logger.error(f"History clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions")
async def get_suggestions(query: str = "") -> List[str]:
    """Get chat suggestions based on query"""
    suggestions = [
        "Tell me about retinol",
        "What's good for acne?",
        "Compare vitamin C and niacinamide",
        "Is this product safe?",
        "Help with dark spots",
        "Recommendations for me",
        "Can I use retinol with vitamin C?",
        "What is hyaluronic acid?",
        "Best moisturizer for sensitive skin",
        "How to start using retinol"
    ]
    
    if query:
        query_lower = query.lower()
        suggestions = [s for s in suggestions if query_lower in s.lower()]
    
    return suggestions[:5]

@router.post("/feedback")
async def submit_feedback(
    user_id: str,
    feedback: Dict[str, Any]
) -> Dict[str, str]:
    """Submit feedback on chatbot responses"""
    try:
        # Store feedback in database (implement as needed)
        logger.info(f"Feedback from {user_id}: {feedback}")
        return {"status": "success", "message": "Thank you for your feedback!"}
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))