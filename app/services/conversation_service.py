"""
Conversation service for managing conversation history and context
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.config import settings


class ConversationService:
    """Service for managing conversation history and context"""
    
    def __init__(self):
        """Initialize the conversation service"""
        self.conversations_dir = Path("data/conversations")
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        self.max_history = settings.MAX_CONVERSATION_HISTORY
        self.timeout = settings.CONVERSATION_TIMEOUT
    
    def create_conversation(self) -> str:
        """
        Create a new conversation
        
        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        conversation_data = {
            "conversation_id": conversation_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        
        self._save_conversation(conversation_id, conversation_data)
        return conversation_id
    
    def add_message(
        self, 
        conversation_id: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a message to a conversation
        
        Args:
            conversation_id: Conversation ID
            role: Message role (user/assistant)
            content: Message content
            metadata: Additional metadata
            
        Returns:
            Message data
        """
        conversation = self._load_conversation(conversation_id)
        if not conversation:
            raise Exception(f"Conversation {conversation_id} not found")
        
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        conversation["messages"].append(message)
        conversation["updated_at"] = datetime.now().isoformat()
        
        # Limit conversation history
        if len(conversation["messages"]) > self.max_history:
            conversation["messages"] = conversation["messages"][-self.max_history:]
        
        self._save_conversation(conversation_id, conversation)
        return message
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of messages
        """
        conversation = self._load_conversation(conversation_id)
        if not conversation:
            return []
        
        return conversation["messages"]
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation summary
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation summary
        """
        conversation = self._load_conversation(conversation_id)
        if not conversation:
            return {}
        
        return {
            "conversation_id": conversation["conversation_id"],
            "created_at": conversation["created_at"],
            "updated_at": conversation["updated_at"],
            "message_count": len(conversation["messages"]),
            "last_message": conversation["messages"][-1] if conversation["messages"] else None
        }
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if deleted, False if not found
        """
        conversation_file = self.conversations_dir / f"{conversation_id}.json"
        if conversation_file.exists():
            conversation_file.unlink()
            return True
        return False
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        List all conversations
        
        Returns:
            List of conversation summaries
        """
        conversations = []
        
        for conversation_file in self.conversations_dir.glob("*.json"):
            try:
                conversation_id = conversation_file.stem
                summary = self.get_conversation_summary(conversation_id)
                if summary:
                    conversations.append(summary)
            except Exception:
                continue
        
        # Sort by updated_at (most recent first)
        conversations.sort(key=lambda x: x["updated_at"], reverse=True)
        return conversations
    
    def cleanup_old_conversations(self) -> int:
        """
        Clean up conversations older than timeout
        
        Returns:
            Number of conversations deleted
        """
        cutoff_time = datetime.now() - timedelta(seconds=self.timeout)
        deleted_count = 0
        
        for conversation_file in self.conversations_dir.glob("*.json"):
            try:
                conversation_id = conversation_file.stem
                conversation = self._load_conversation(conversation_id)
                
                if conversation:
                    updated_at = datetime.fromisoformat(conversation["updated_at"])
                    if updated_at < cutoff_time:
                        conversation_file.unlink()
                        deleted_count += 1
                        
            except Exception:
                continue
        
        return deleted_count
    
    def get_conversation_context(
        self, 
        conversation_id: str, 
        max_messages: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get conversation context for LLM
        
        Args:
            conversation_id: Conversation ID
            max_messages: Maximum number of messages to include
            
        Returns:
            Formatted conversation context
        """
        messages = self.get_conversation_history(conversation_id)
        
        # Take the last max_messages
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
        
        # Format for LLM
        context = []
        for message in recent_messages:
            context.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        return context
    
    def _load_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Load conversation from file
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data or None
        """
        conversation_file = self.conversations_dir / f"{conversation_id}.json"
        
        if not conversation_file.exists():
            return None
        
        try:
            with open(conversation_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _save_conversation(self, conversation_id: str, conversation_data: Dict[str, Any]):
        """
        Save conversation to file
        
        Args:
            conversation_id: Conversation ID
            conversation_data: Conversation data
        """
        conversation_file = self.conversations_dir / f"{conversation_id}.json"
        
        try:
            with open(conversation_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Failed to save conversation: {str(e)}")


# Create global conversation service instance
conversation_service = ConversationService() 