#!/usr/bin/env python3

import os
import sys
import subprocess


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Running in normal Python environment
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)
from ai_tutor import AITutor
from terminal_interface import TerminalInterface
from config import Config
from core.logger import create_logger
from core.error_handler import safe_execute

class AIPairProgrammingTutor:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.running = False
        
        # Create logger
        self.logger = create_logger("ai_tutor", debug=debug, 
                                  log_file="ai_tutor.log" if not debug else None)
        
        # Initialize core components directly
        self.ui = TerminalInterface()
        self.config = Config()
        self.ai_tutor = None
        
        # Initialize AI tutor
        self._init_ai_tutor()
    
    def _init_ai_tutor(self):
        """Initialize AI tutor component"""
        def init_ai_tutor():
            self.ai_tutor = AITutor(self.config, self.ui)
            provider = self.config.get_current_provider()
            model = self.config.get_model_for_provider(provider)
            self.logger.info(f"AI Tutor initialized (Provider: {provider}, Model: {model})")
            self.ui.show_success(f"AI Tutor initialized (Provider: {provider}, Model: {model})")
            return True
        
        result = safe_execute(init_ai_tutor, context="AI Tutor initialization", default_return=False)
        if not result:
            self.ui.show_error("Failed to initialize AI Tutor. Check logs for details.")


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
        
        # Auto-save conversation after each exchange
        self.auto_save_conversation()

    def process_simple_ask(self, user_input: str):
        """Process user input using simple tutor (non-Socratic) approach"""
        if not self.ai_tutor:
            self.ui.show_error("AI Tutor not available")
            return

        self.ui.show_processing_indicator()

        # Get context about current directory/files for better responses
        context = self._get_current_context()

        # Get AI response using simple tutor
        ai_response = self.ai_tutor.get_simple_response(user_input, context)

        # Display the response
        self.ui.show_ai_response(ai_response)
        
        # Auto-save conversation after each exchange
        self.auto_save_conversation()

    def process_raw_prompt(self, user_input: str):
        """Process user input as a completely raw prompt (no system prompt)"""
        if not self.ai_tutor:
            self.ui.show_error("AI Tutor not available")
            return

        self.ui.show_processing_indicator()

        # Get context about current directory/files for better responses
        context = self._get_current_context()

        # Get AI response using raw prompt (no system prompt)
        ai_response = self.ai_tutor.get_raw_response(user_input, context)

        # Display the response
        self.ui.show_ai_response(ai_response)
        
        # Auto-save conversation after each exchange
        self.auto_save_conversation()

    def execute_bash_command(self, command: str):
        """Execute a bash command and display the output"""
        try:
            self.ui.show_info(f"Executing: {command}")
            
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            # Display output
            if result.stdout:
                self.ui.show_success("Command Output:")
                self.ui.console.print(result.stdout)
            
            if result.stderr:
                self.ui.show_error("Command Error:")
                self.ui.console.print(result.stderr)
            
            if result.returncode != 0:
                self.ui.show_error(f"Command exited with code: {result.returncode}")
            else:
                self.ui.show_success(f"Command completed successfully (exit code: 0)")
                
        except subprocess.TimeoutExpired:
            self.ui.show_error("Command timed out after 30 seconds")
        except Exception as e:
            self.ui.show_error(f"Failed to execute command: {e}")

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
        
        # Check if it's a bash command (starts with !)
        if user_input.startswith('!'):
            bash_command = user_input[1:].strip()
            if bash_command:
                self.execute_bash_command(bash_command)
            else:
                self.ui.show_info("Usage: !<command> - Execute bash command")
            return
        
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

            elif command.startswith('provider '):
                # Switch AI provider
                provider = command[9:].strip().lower()
                self.switch_provider(provider)

            elif command == 'config':
                # Show current configuration
                self.show_config()

            elif command == 'log':
                # Show conversation log
                self.show_conversation_log()

            elif command.startswith('log '):
                # Save conversation log to file
                args = command[4:].strip()
                if args == 'save':
                    self.save_conversation_log()
                else:
                    self.ui.show_info("Usage: /log or /log save")

            elif command == 'resume':
                # List available conversation logs
                self.list_conversation_logs()

            elif command.startswith('resume '):
                # Resume from specific conversation log
                filename = command[7:].strip()
                if filename == 'latest':
                    filename = 'latest.jsonl'
                self.resume_conversation(filename)

            elif command.startswith('role '):
                # Switch system prompt role
                role = command[5:].strip().lower()
                self.switch_role(role)

            elif command.startswith('ask '):
                # Use simple tutor for direct question
                question = command[4:].strip()
                if question:
                    self.process_simple_ask(question)
                else:
                    self.ui.show_info("Usage: /ask <your question>")

            elif command.startswith('prompt '):
                # Use completely raw prompt (no system prompt)
                raw_prompt = command[7:].strip()
                if raw_prompt:
                    self.process_raw_prompt(raw_prompt)
                else:
                    self.ui.show_info("Usage: /prompt <your raw prompt>")

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

    def switch_role(self, role: str):
        """Switch the AI tutor's role/system prompt"""
        try:
            if not self.ai_tutor:
                self.ui.show_error("AI tutor not initialized yet.")
                return
            
            success = self.ai_tutor.switch_role(role)
            if success:
                if role == "tutor":
                    self.ui.show_success("Switched to Socratic tutor mode")
                elif role == "simple":
                    self.ui.show_success("Switched to simple tutor mode")
                elif role == "short":
                    self.ui.show_success("Switched to short response mode")
            else:
                self.ui.show_error(f"Unknown role: '{role}'. Available roles: tutor, simple, short")
                
        except Exception as e:
            self.ui.show_error(f"Failed to switch role: {e}")

    def show_conversation_log(self):
        """Show conversation history"""
        try:
            if not self.ai_tutor:
                self.ui.show_info("AI tutor not initialized yet.")
                return
                
            messages = self.ai_tutor.get_conversation_history()
            
            if not messages:
                self.ui.show_info("No conversation history yet.")
                return
            
            log_output = f"Conversation Log ({len(messages)} messages):\n\n"
            
            for i, msg in enumerate(messages, 1):
                if msg["role"] == "user":
                    role = "User"
                elif msg["role"] == "assistant":
                    role = "AI"
                else:
                    role = msg["role"].title()
                
                content = msg["content"]
                log_output += f"[{i}] {role}: {content}\n\n"
            
            self.ui.show_info(log_output.strip())
            
        except Exception as e:
            self.ui.show_error(f"Failed to show conversation log: {e}")

    def save_conversation_log(self):
        """Save conversation history to file"""
        try:
            if not self.ai_tutor:
                self.ui.show_info("AI tutor not initialized yet.")
                return
                
            messages = self.ai_tutor.get_conversation_history()
            
            if not messages:
                self.ui.show_info("No conversation history to save.")
                return
            
            # Create config directory if it doesn't exist
            from pathlib import Path
            import datetime
            
            config_dir = Path.home() / ".config" / "ai-tutor"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_log_{timestamp}.jsonl"
            filepath = config_dir / filename
            
            # Save conversation as JSONL
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write metadata header
                header = {
                    "type": "metadata",
                    "title": "AI Tutor Conversation Log",
                    "saved": datetime.datetime.now().isoformat(),
                    "message_count": len(messages)
                }
                f.write(json.dumps(header) + '\n')
                
                # Write each message as a JSON line
                for i, msg in enumerate(messages):
                    log_entry = {
                        "type": "message",
                        "index": i + 1,
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    f.write(json.dumps(log_entry) + '\n')
            
            self.ui.show_success(f"Conversation log saved to: {filepath}")
            
        except Exception as e:
            self.ui.show_error(f"Failed to save conversation log: {e}")

    def auto_save_conversation(self):
        """Auto-save conversation to latest.txt"""
        try:
            if not self.ai_tutor:
                return
                
            messages = self.ai_tutor.get_conversation_history()
            
            if not messages:
                return
            
            # Create config directory if it doesn't exist
            from pathlib import Path
            import datetime
            
            config_dir = Path.home() / ".config" / "ai-tutor"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = config_dir / "latest.jsonl"
            
            # Save conversation as JSONL
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write metadata header
                header = {
                    "type": "metadata",
                    "title": "AI Tutor Conversation Log (Auto-saved)",
                    "last_updated": datetime.datetime.now().isoformat(),
                    "message_count": len(messages)
                }
                f.write(json.dumps(header) + '\n')
                
                # Write each message as a JSON line
                for i, msg in enumerate(messages):
                    log_entry = {
                        "type": "message",
                        "index": i + 1,
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    f.write(json.dumps(log_entry) + '\n')
            
        except Exception:
            # Silently fail auto-save to not interrupt user experience
            pass

    def list_conversation_logs(self):
        """List available conversation log files"""
        try:
            from pathlib import Path
            import os
            
            config_dir = Path.home() / ".config" / "ai-tutor"
            
            if not config_dir.exists():
                self.ui.show_info("No conversation logs directory found.")
                return
            
            # Find all conversation log files (both old .txt and new .jsonl)
            log_files = list(config_dir.glob("conversation_log_*.txt")) + list(config_dir.glob("conversation_log_*.jsonl"))
            
            if not log_files:
                self.ui.show_info("No conversation logs found.")
                return
            
            # Sort by modification time (newest first)
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            logs_info = "Available conversation logs:\n\n"
            for i, log_file in enumerate(log_files, 1):
                # Get file info
                stat = log_file.stat()
                import datetime
                mod_time = datetime.datetime.fromtimestamp(stat.st_mtime)
                size = stat.st_size
                
                logs_info += f"[{i}] {log_file.name}\n"
                logs_info += f"    Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                logs_info += f"    Size: {size} bytes\n\n"
            
            logs_info += "Usage: /resume <filename> to load a conversation"
            self.ui.show_info(logs_info.strip())
            
        except Exception as e:
            self.ui.show_error(f"Failed to list conversation logs: {e}")

    def resume_conversation(self, filename: str):
        """Resume conversation from log file"""
        try:
            if not self.ai_tutor:
                self.ui.show_info("AI tutor not initialized yet.")
                return
            
            from pathlib import Path
            import json
            
            config_dir = Path.home() / ".config" / "ai-tutor"
            filepath = config_dir / filename
            
            if not filepath.exists():
                self.ui.show_error(f"Conversation log file not found: {filename}")
                return
            
            # Clear current conversation
            self.ai_tutor.clear_conversation()
            
            # Parse based on file extension
            if filename.endswith('.jsonl'):
                # Parse JSONL format
                loaded_count = 0
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            entry = json.loads(line)
                            
                            # Skip metadata entries
                            if entry.get("type") == "metadata":
                                continue
                            
                            # Load message entries
                            if entry.get("type") == "message":
                                self.ai_tutor.conversation_history.append({
                                    "role": entry["role"],
                                    "content": entry["content"]
                                })
                                loaded_count += 1
                                
                        except json.JSONDecodeError as e:
                            self.ui.show_error(f"Invalid JSON on line {line_num}: {e}")
                            return
            
            else:
                # Legacy .txt format parsing (for backward compatibility)
                self._parse_legacy_log_format(filepath)
                loaded_count = len(self.ai_tutor.conversation_history)
            
            self.ui.show_success(f"Resumed conversation from {filename}")
            self.ui.show_info(f"Loaded {loaded_count} messages from conversation log")
            
        except Exception as e:
            self.ui.show_error(f"Failed to resume conversation: {e}")

    def _parse_legacy_log_format(self, filepath):
        """Parse legacy .txt format logs"""
        import re
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and header lines
            if not line or line.startswith("AI Tutor Conversation") or line.startswith("Saved:") or line.startswith("Last updated:"):
                i += 1
                continue
            
            # Skip tool metadata lines (legacy format compatibility)
            if line.startswith("    [Tool]"):
                i += 1
                continue
            
            # Check for numbered conversation entries
            pattern = r'^\[(\d+)\] (User|AI): (.*)$'
            match = re.match(pattern, line)
            if match:
                number, role, message_start = match.groups()
                role_key = "user" if role == "User" else "assistant"
                
                # Collect multi-line message content
                message_lines = [message_start]
                i += 1
                
                # Continue reading until we hit another numbered entry, tool metadata, or end
                while i < len(lines):
                    next_line = lines[i]
                    if (re.match(r'^\[\d+\]', next_line.strip()) or 
                        next_line.strip().startswith("    [Tool]") or 
                        not next_line.strip()):
                        break
                    message_lines.append(next_line)
                    i += 1
                
                # Join message content and add to history
                full_message = '\n'.join(message_lines).strip()
                self.ai_tutor.conversation_history.append({
                    "role": role_key,
                    "content": full_message
                })
            else:
                i += 1

    def run(self):
        """Main application loop"""
        # self.ui.clear_screen()
        self.ui.show_welcome()

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
        print("\nUsage: ai [--debug] [--help]")
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
