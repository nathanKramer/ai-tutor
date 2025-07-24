import openai
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class AITutor:
    def __init__(self, api_key: Optional[str] = None):
        self.client = openai.OpenAI(
            api_key=api_key or os.getenv('OPENAI_API_KEY')
        )
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = """You are an AI programming tutor engaged in pair programming. 
The human is in the driver's seat - they write the code while you provide guidance, suggestions, and explanations.

Your role:
- Provide helpful guidance and suggestions
- Explain concepts when asked
- Help debug issues
- Suggest best practices
- Ask clarifying questions
- Be encouraging and supportive

Keep responses conversational and concise since they'll be spoken aloud. 
Focus on being a helpful pair programming partner, not taking over the coding."""
    
    def get_response(self, user_input: str, context: str = "") -> str:
        """
        Get AI tutor response to user input
        
        Args:
            user_input: What the user said
            context: Additional context about current code/situation
            
        Returns:
            AI tutor's response
        """
        try:
            # Add context to the message if provided
            message_content = user_input
            if context:
                message_content = f"Context: {context}\n\nUser: {user_input}"
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user", 
                "content": message_content
            })
            
            # Prepare messages for API call
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Include recent conversation history (last 10 messages to manage token usage)
            recent_history = self.conversation_history[-10:]
            messages.extend(recent_history)
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Add AI response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })
            
            return ai_response
            
        except openai.AuthenticationError:
            return "I need an OpenAI API key to work. Please set your OPENAI_API_KEY environment variable."
        except openai.RateLimitError:
            return "I'm getting rate limited. Please wait a moment before trying again."
        except Exception as e:
            return f"I encountered an error: {str(e)}"
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt"""
        self.system_prompt = prompt
    
    def get_conversation_summary(self) -> str:
        """Get a summary of recent conversation"""
        if not self.conversation_history:
            return "No conversation yet."
        
        recent_messages = self.conversation_history[-4:]
        summary = "Recent conversation:\n"
        for msg in recent_messages:
            role = "You" if msg["role"] == "user" else "AI Tutor"
            summary += f"{role}: {msg['content'][:100]}...\n"
        
        return summary