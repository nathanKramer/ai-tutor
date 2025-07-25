#!/usr/bin/env python3

import os
import sys
from ai_tutor import AITutor
from terminal_interface import TerminalInterface
from config import Config

class AIPairProgrammingTutor:
    def __init__(self, debug: bool = False):
        self.ui = TerminalInterface()
        self.config = Config()
        self.ai_tutor = None
        self.running = False
        self.debug = debug

        # Initialize components
        self._init_components()

    def _init_components(self):
        """Initialize all system components"""
        try:
            self.ai_tutor = AITutor(self.config, self.ui)
            provider = self.config.get_current_provider()
            model = self.config.get_model_for_provider(provider)
            self.ui.show_success(f"AI Tutor initialized (Provider: {provider}, Model: {model})")
        except Exception as e:
            self.ui.show_error(f"Failed to initialize AI Tutor: {e}")


    def process_user_input(self, user_input: str):
        """Process user input and get AI response"""
        if not self.ai_tutor:
            self.ui.show_error("AI Tutor not available")
            return

        self.ui.show_processing_indicator()

        # Get context about current directory/files for better responses
        context = self._get_current_context()

        # Get AI response
        ai_response = self.ai_tutor.get_response(user_input, context)

        # Display the response
        self.ui.show_ai_response(ai_response)

    def _get_current_context(self) -> str:
        """Get context about current working directory"""
        try:
            cwd = os.getcwd()
            files = [f for f in os.listdir(cwd) if f.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.css'))]

            context = f"Current directory: {os.path.basename(cwd)}"
            if files:
                context += f"\nCode files present: {', '.join(files[:5])}"
                if len(files) > 5:
                    context += f" and {len(files) - 5} more"

            return context
        except Exception:
            return "Working in current directory"

    def handle_text_command(self, user_input: str):
        """Handle text-based commands or direct messages"""
        user_input = user_input.strip()
        
        # Check if it's a command (starts with /)
        if user_input.startswith('/'):
            command = user_input[1:].lower().strip()
            
            if command in ['quit', 'exit']:
                self.running = False
                return

            elif command == 'help':
                self.ui.show_help()

            elif command == 'clear':
                if self.ai_tutor:
                    self.ai_tutor.clear_conversation()
                    self.ui.show_success("Conversation history cleared")

            elif command == 'status':
                self.ui.show_status(
                    ai_available=self.ai_tutor is not None
                )

            elif command.startswith('provider '):
                # Switch AI provider
                provider = command[9:].strip().lower()
                self.switch_provider(provider)

            elif command == 'config':
                # Show current configuration
                self.show_config()

            else:
                self.ui.show_info(f"Unknown command: /{command}. Type '/help' for available commands.")
        
        else:
            # Not a command - treat as direct message to AI
            if user_input:
                self.process_user_input(user_input)
    
    def switch_provider(self, provider: str):
        """Switch AI provider"""
        try:
            if provider not in ["openai", "claude"]:
                self.ui.show_error(f"Unsupported provider: {provider}. Available: openai, claude")
                return
            
            # Check if API key is available for the provider
            api_key = self.config.get_api_key(provider)
            if not api_key:
                env_var = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
                self.ui.show_error(f"No API key found for {provider}. Please set {env_var} environment variable.")
                return
            
            # Switch provider using AITutor's method
            if self.ai_tutor and self.ai_tutor.switch_provider(provider):
                model = self.config.get_model_for_provider(provider)
                self.ui.show_success(f"Switched to {provider} (Model: {model})")
            else:
                self.ui.show_error(f"Failed to switch to {provider}. Provider may not be available.")
            
        except Exception as e:
            self.ui.show_error(f"Failed to switch provider: {e}")
    
    def show_config(self):
        """Show current configuration"""
        try:
            provider = self.config.get_current_provider()
            model = self.config.get_model_for_provider(provider)
            max_tokens = self.config.get("max_tokens")
            temperature = self.config.get("temperature")
            
            config_info = f"""Current Configuration:
• Provider: {provider}
• Model: {model}
• Max Tokens: {max_tokens}
• Temperature: {temperature}
• History Limit: {self.config.get("conversation_history_limit")}

Available Commands:
• /provider openai - Switch to OpenAI
• /provider claude - Switch to Claude"""
            
            self.ui.show_info(config_info)
            
        except Exception as e:
            self.ui.show_error(f"Failed to show config: {e}")


    def run(self):
        """Main application loop"""
        # self.ui.clear_screen()
        self.ui.show_welcome()

        # Check component availability
        self.ui.show_status(
            ai_available=self.ai_tutor is not None
        )

        self.running = True

        try:
            while self.running:
                try:
                    # Get user input
                    user_input = self.ui.get_user_input()

                    if user_input.strip():
                        self.handle_text_command(user_input)

                except KeyboardInterrupt:
                    break
                except EOFError:
                    break

        except Exception as e:
            self.ui.show_error(f"Unexpected error: {e}")

        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        self.ui.show_goodbye()

def main():
    """Entry point"""
    debug = '--debug' in sys.argv

    if len(sys.argv) > 1 and '--help' in sys.argv:
        print("AI Pair Programming Tutor")
        print("\nUsage: python main.py [--debug] [--help]")
        print("\nOptions:")
        print("  --debug    Enable debug output")
        print("  --help     Show this help message")
        print("\nRequires:")
        print("- At least one API key:")
        print("  • OPENAI_API_KEY for OpenAI GPT models")
        print("  • ANTHROPIC_API_KEY for Claude models")
        return

    # Check for API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    claude_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not openai_key and not claude_key:
        print("⚠️  Warning: No API keys found.")
        print("   Set at least one API key:")
        print("   - OpenAI: export OPENAI_API_KEY='your-key-here'")
        print("   - Claude: export ANTHROPIC_API_KEY='your-key-here'")
        input("Press Enter to continue anyway...")
    elif not openai_key:
        print("ℹ️  Note: OPENAI_API_KEY not set - OpenAI provider will be unavailable")
    elif not claude_key:
        print("ℹ️  Note: ANTHROPIC_API_KEY not set - Claude provider will be unavailable")

    tutor = AIPairProgrammingTutor(debug=debug)
    tutor.run()

if __name__ == "__main__":
    main()
