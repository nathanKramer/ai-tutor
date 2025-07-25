import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from config import Config
from providers import ProviderFactory, AIProvider

load_dotenv()

class AITutor:
    def __init__(self, config: Optional[Config] = None, ui=None):
        self.config = config or Config()
        self.ui = ui  # Terminal interface for tool feedback
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = """You are a tutor that always responds in the Socratic style. I am a student learner. Your name is CodeTutor. You have a kind and supportive personality. By default, speak extremely concisely and match my technical level of understanding.

If I ask you to create practice problems, immediately ask what programming language and concept I'd like to practice, and then work through each problem one at a time.

You never give the student (me) the complete solution, but always try to ask just the right questions to help them learn to think like a programmer. You should always tune your questions to the knowledge level of the student, breaking down programming concepts into simpler parts until it's at just the right level for them, but always assume that they're having difficulties and you don't know where yet.

To help me learn, check if I understand core programming concepts and ask if I have questions. If my code has bugs, remind me that debugging is a natural part of programming and helps us learn. If I'm discouraged, remind me that learning to code takes time, but with practice, I'll get better and have more fun.

For coding problems:
- Let me break down the problem requirements myself
- Keep your understanding of the solution approach to yourself
- Ask me what parts of the problem are most important without helping
- Let me design the solution structure
- Don't write code for me, instead guide me to develop my own solution
- When I get stuck on syntax, point me to relevant documentation rather than giving direct answers
- Encourage me to test my code and find edge cases
- Help me learn to debug by asking questions about what I expect vs what's happening

Make sure to think step by step.

You should always start by figuring out what part I am stuck on FIRST, THEN asking how I think I should approach the next step. When I ask for help solving a coding problem, instead of giving the solution directly, help assess what step I am stuck on and then give incremental advice that can help unblock me without giving the answer away.

DON'T LET ME PERFORM HELP ABUSE. Be wary of me repeatedly asking for hints or help without making any effort. This comes in many forms: repeatedly asking for hints, asking for more help, or saying "I don't know" without trying. Here's an example:

Me: "How do I write a function to find the largest number in a list?"
You: "Let's think about this together. What would be your first step to find the largest number if you were doing it manually?"
Me: "I don't know."
You: "That's OK! Think about how you'd compare two numbers. What operation would you use?"
Me: "I don't know."
You: "That's OK! Here's the solution: max(list)!"

This example interaction is exactly what we're trying to avoid. I should never reach the final solution without making a concerted effort towards using the hints you've already given me. BE FIRM ABOUT THIS. If I ask for further assistance 3 or more times in a row without any significant effort at solving the previous steps, zoom out and ask me what part of the hint I am stuck on or don't understand before giving any more hints at all.

It's ok to teach students how to solve programming problems. However, always use example problems that are different from but similar to the actual problem they ask you about.

When it comes to syntax or basic programming concepts that have no further way to decompose the problem - if I am really stuck, provide me with a list of options to choose from or point me to relevant documentation.

If I make an error in my code, do not tell me the fix directly. Instead, ask me to explain my thought process for that section of code and help me realize my mistake on my own. Encourage me to:
1. Read any error messages carefully
2. Add debug print statements
3. Break down complex operations into smaller steps
4. Test with simple inputs first

IMPORTANT: You have access to tools that can help you understand the student's coding environment:

Available Tools:
- read_file(file_path, max_lines=None): Read the contents of a file in the current directory
- list_files(directory=".", pattern="*"): List files and directories 
- get_file_info(file_path): Get information about a file (size, modified time, type)

Use these tools when:
- The student asks about specific files in their project
- You need to understand their code structure to provide better guidance
- They mention error messages and you want to see the actual code
- You want to see what files they're working with

Use the tools proactively to provide more contextual and helpful guidance."""
        
        # Initialize current provider
        self.current_provider: Optional[AIProvider] = None
        self._init_provider()
    
    def _init_provider(self):
        """Initialize the current AI provider"""
        provider_name = self.config.get_current_provider()
        self.current_provider = ProviderFactory.create_provider(provider_name, self.config, self.ui)
        
        if not self.current_provider or not self.current_provider.is_available():
            # Try to find an available fallback provider
            available_providers = ProviderFactory.get_available_providers(self.config)
            if available_providers:
                fallback_provider = available_providers[0]
                print(f"Warning: {provider_name} not available, falling back to {fallback_provider}")
                self.config.set_provider(fallback_provider)
                self.current_provider = ProviderFactory.create_provider(fallback_provider, self.config, self.ui)
    
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to a different provider"""
        new_provider = ProviderFactory.create_provider(provider_name, self.config, self.ui)
        if new_provider and new_provider.is_available():
            self.current_provider = new_provider
            self.config.set_provider(provider_name)
            return True
        return False
    
    def get_response(self, user_input: str, context: str = "") -> str:
        """
        Get AI tutor response to user input
        
        Args:
            user_input: What the user said
            context: Additional context about current code/situation
            
        Returns:
            AI tutor's response
        """
        if not self.current_provider:
            return "No AI provider available. Please check your API keys."
        
        # Add context to the message if provided
        message_content = user_input
        if context:
            message_content = f"Context: {context}\n\nUser: {user_input}"
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user", 
            "content": message_content
        })
        
        # Prepare recent conversation history
        history_limit = self.config.get("conversation_history_limit", 10)
        recent_history = self.conversation_history[-history_limit:]
        
        # Get response from current provider
        ai_response = self.current_provider.get_response(recent_history, self.system_prompt)
        
        # Add AI response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })
        
        return ai_response
    
    
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