from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
import time
import sys
from typing import Optional
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

class TerminalInterface:
    def __init__(self):
        self.console = Console()
        
    def show_welcome(self):
        """Display welcome message"""
        welcome_text = """
🤖 AI Programming Tutor

Welcome to your AI pair programming partner!

How to Use:
• Just type your messages directly - no need for commands!
• Press Enter for new lines, Alt+Enter to submit
• Use /command for system commands (e.g., /help, /quit)
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
        
    def show_ai_response(self, text: str):
        """Display AI response in a formatted way"""
        response_panel = Panel(
            text,
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
        help_table.add_row("/provider <name>", "Switch AI provider (openai, claude)")
        help_table.add_row("/config", "Show current configuration")
        help_table.add_row("/help", "Show this help message")
        help_table.add_row("/clear", "Clear conversation history")
        help_table.add_row("/status", "Show system status")
        help_table.add_row("/quit or /exit", "End the tutoring session")
        
        self.console.print(help_table)
    
    def show_status(self, ai_available: bool):
        """Show system component status"""
        status_table = Table(title="System Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="white")
        
        ai_status = "✅ Available" if ai_available else "❌ Not Available"
        
        status_table.add_row("AI Tutor", ai_status)
        
        self.console.print(status_table)
    
    def get_user_input(self, prompt_text: str = "> ") -> str:
        """Get text input from user with multi-line support"""
        
        try:
            # Show instruction
            self.console.print("[dim]💡 Tip: Type directly to chat, use /help to view available commands. Press Enter for new lines, Alt+Enter to submit[/dim]")
            
            # Use prompt-toolkit's built-in multiline functionality
            # By default: Enter submits, Meta+Enter (Alt+Enter) or Escape+Enter adds newlines
            result = prompt(
                prompt_text,
                multiline=True,
                wrap_lines=True
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
