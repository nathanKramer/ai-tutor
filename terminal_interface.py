from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.syntax import Syntax
from rich.markdown import Markdown
import time
import sys
import re
from typing import Optional
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.application import get_app

class TerminalInterface:
    def __init__(self):
        self.console = Console()
        self.last_ctrl_c_time = 0
        
    def show_welcome(self):
        """Display welcome message"""
        welcome_text = """
🤖 AI Programming Tutor

Welcome to your AI pair programming partner!

How to Use:
• Type messages to the tutor
• Press Enter for new lines, Alt+Enter to submit
• Type /help to see all available commands

Ready to start coding together! 🚀
        """
        
        panel = Panel(
            welcome_text.strip(),
            title="[bold blue]AI Tutor Session[/bold blue]",
            border_style="blue"
        )
        self.console.print(panel)
    
    
    def show_processing_indicator(self):
        """Show that speech is being processed"""
        self.console.print("🔄 [yellow]Processing your request...[/yellow]")
        
    def _parse_and_render_content(self, text: str):
        """Parse text for code blocks and render with syntax highlighting"""
        # Pattern to match code blocks with optional language specifier
        code_block_pattern = r'```(\w+)?\n(.*?)\n```'
        
        # Find all code blocks
        matches = list(re.finditer(code_block_pattern, text, re.DOTALL))
        
        if not matches:
            # No code blocks found, return as regular text
            return text
        
        # Process text with code blocks
        result_parts = []
        last_end = 0
        
        for match in matches:
            # Add text before code block
            if match.start() > last_end:
                before_text = text[last_end:match.start()].rstrip()
                if before_text:
                    result_parts.append(before_text)
            
            # Extract language and code
            language = match.group(1) if match.group(1) else 'text'
            code = match.group(2)
            
            # Create syntax highlighted code block
            try:
                syntax = Syntax(
                    code, 
                    lexer=language, 
                    theme="monokai",
                    line_numbers=True,
                    padding=1
                )
                result_parts.append(syntax)
            except Exception:
                # Fallback to plain text if syntax highlighting fails
                result_parts.append(f"```{language}\n{code}\n```")
            
            last_end = match.end()
        
        # Add remaining text after last code block
        if last_end < len(text):
            remaining_text = text[last_end:].lstrip()
            if remaining_text:
                result_parts.append(remaining_text)
        
        return result_parts

    def show_ai_response(self, text: str):
        """Display AI response in a formatted way with syntax highlighting"""
        content = self._parse_and_render_content(text)
        
        if isinstance(content, list):
            # Multiple parts (text + code blocks) - show title panel first
            title_panel = Panel(
                "",
                title="[bold cyan]🤖 AI Tutor[/bold cyan]",
                border_style="cyan",
                padding=(0, 0),
                height=1
            )
            self.console.print(title_panel)
            
            for i, part in enumerate(content):
                if isinstance(part, Syntax):
                    # Add some spacing before code blocks
                    if i > 0:
                        self.console.print()
                    self.console.print(part)
                else:
                    # Regular text - add padding to match panel style
                    if part.strip():
                        text_content = Text(part.strip())
                        if text_content:
                            text_panel = Panel(
                                text_content,
                                border_style="cyan",
                                padding=(0, 2)
                            )
                            self.console.print(text_panel)
        else:
            # Single part (no code blocks)
            response_panel = Panel(
                content,
                title="[bold cyan]🤖 AI Tutor[/bold cyan]",
                border_style="cyan",
                padding=(1, 2)
            )
            self.console.print(response_panel)
    
    def show_user_input(self, text: str):
        """Display what user said"""
        if '\n' in text:
            # Multi-line input - use a panel for better formatting
            user_panel = Panel(
                text,
                title="[bold white]👤 Your Input[/bold white]",
                border_style="blue",
                padding=(0, 1)
            )
            self.console.print(user_panel)
        else:
            # Single line input - simple format
            user_text = Text(f"👤 You said: {text}", style="bold white")
            self.console.print(user_text)
    
    def show_error(self, error_msg: str):
        """Display error message"""
        error_panel = Panel(
            f"❌ {error_msg}",
            title="[bold red]Error[/bold red]",
            border_style="red"
        )
        self.console.print(error_panel)
    
    def show_info(self, info_msg: str):
        """Display info message"""
        self.console.print(f"ℹ️  [blue]{info_msg}[/blue]")
    
    def show_success(self, success_msg: str):
        """Display success message"""
        self.console.print(f"✅ [green]{success_msg}[/green]")
    
    def show_help(self):
        """Display help information"""
        help_table = Table(title="Available Commands")
        help_table.add_column("Command", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="white")
        
        help_table.add_row("Direct messaging", "Just type your message and press Alt+Enter to submit")
        help_table.add_row("Multi-line input", "Press Enter for new lines, Alt+Enter to submit")
        help_table.add_row("/ask <question>", "Ask a direct question (uses simple tutor, not Socratic)")
        help_table.add_row("/provider <name>", "Switch AI provider (openai, claude)")
        help_table.add_row("/config", "Show current configuration")
        help_table.add_row("/help", "Show this help message")
        help_table.add_row("/clear", "Clear conversation history")
        help_table.add_row("/quit or /exit", "End the tutoring session")
        
        self.console.print(help_table)
    
    def get_user_input(self, prompt_text: str = "> ") -> str:
        """Get text input from user with multi-line support and Ctrl+C handling"""
        
        # Create custom key bindings
        bindings = KeyBindings()
        
        @bindings.add('c-c')
        def _(event):
            """Handle Ctrl+C - clear text or show warning"""
            current_time = time.time()
            
            # If there's text in the buffer, clear it
            if event.app.current_buffer.text:
                event.app.current_buffer.reset()
                self.console.print("🧹 [yellow]Press Ctrl+C again within 1 second to exit.[/yellow]")
                self.last_ctrl_c_time = current_time
            else:
                # No text in buffer, check if we should exit
                if current_time - self.last_ctrl_c_time <= 1.0:
                    # Second Ctrl+C within 1 second, exit
                    event.app.exit(exception=KeyboardInterrupt())
                else:
                    # First Ctrl+C with empty buffer, show warning
                    self.console.print("⚠️  [yellow]Press Ctrl+C again within 1 second to exit.[/yellow]")
                    self.last_ctrl_c_time = current_time
        
        try:
            # Use prompt-toolkit's built-in multiline functionality
            # By default: Alt Enter submits, Enter adds new lines.
            result = prompt(
                prompt_text,
                multiline=True,
                wrap_lines=True,
                key_bindings=bindings
            )
            
            return result.strip()
            
        except KeyboardInterrupt:
            raise
        except EOFError:
            return ""
    
    def clear_screen(self):
        """Clear the terminal screen"""
        self.console.clear()
    
    def show_goodbye(self):
        """Display goodbye message"""
        goodbye_text = """
Thanks for using AI Tutor! 
Happy coding! 🎉
        """
        
        panel = Panel(
            goodbye_text.strip(),
            title="[bold green]Session Ended[/bold green]",
            border_style="green"
        )
        self.console.print(panel)
