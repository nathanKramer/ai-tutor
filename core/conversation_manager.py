from typing import List, Dict
from core.interfaces import ConversationManagerInterface


class InMemoryConversationManager(ConversationManagerInterface):
    """In-memory conversation history manager"""
    
    def __init__(self, max_history: int = 50):
        self._messages: List[Dict[str, str]] = []
        self._max_history = max_history
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history"""
        message = {"role": role, "content": content}
        self._messages.append(message)
        
        # Trim history if it gets too long
        if len(self._messages) > self._max_history:
            # Keep the most recent messages
            self._messages = self._messages[-self._max_history:]
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent messages from conversation"""
        return self._messages[-limit:] if limit > 0 else self._messages
    
    def clear(self) -> None:
        """Clear conversation history"""
        self._messages.clear()
    
    def get_summary(self) -> str:
        """Get conversation summary"""
        if not self._messages:
            return "No conversation yet."
        
        # Simple summary - show last few exchanges
        recent = self.get_recent_messages(4)
        summary = "Recent conversation:\n"
        
        for msg in recent:
            role = "You" if msg["role"] == "user" else "AI"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            summary += f"{role}: {content}\n"
        
        return summary.strip()
    
    def get_message_count(self) -> int:
        """Get total number of messages"""
        return len(self._messages)
    
    def get_all_messages(self) -> List[Dict[str, str]]:
        """Get all messages (be careful with memory usage)"""
        return self._messages.copy()
    
    def remove_last_message(self) -> bool:
        """Remove the last message from history"""
        if self._messages:
            self._messages.pop()
            return True
        return False
    
    def set_max_history(self, max_history: int) -> None:
        """Set maximum history length"""
        self._max_history = max_history
        
        # Trim current history if needed
        if len(self._messages) > max_history:
            self._messages = self._messages[-max_history:]