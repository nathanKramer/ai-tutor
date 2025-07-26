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
from prompt_toolkit.completion import Completer, Completion, PathCompleter

class CommandCompleter(Completer):
    """Custom completer for AI tutor commands and file paths"""
    
    def __init__(self):
        self.commands = [
            '/ask',
            '/prompt',
            '/provider',
            '/config', 
            '/help',
            '/log',
            '/resume',
            '/role',
            '/clear',
            '/quit',
            '/exit'
        ]
        
        # Create path completer for files and folders
        self.path_completer = PathCompleter()
        
        # Provider-specific completions
        self.provider_commands = [
            '/provider openai',
            '/provider claude'
        ]
        
        # Role-specific completions
        self.role_commands = [
            '/role tutor',
            '/role simple'
        ]
    
    def _extract_path_at_cursor(self, text, cursor_pos):
        """Extract potential file path at cursor position"""
        import re
        
        # Find word boundaries around the cursor
        if cursor_pos == 0:
            return None, 0, 0
            
        # Look for path-like patterns: starts with ./ or / or ~ or contains /
        # Also look for file extensions
        path_pattern = r'[./~\w\-]*[./][./\w\-]*'
        
        # Find all potential paths in the text
        matches = list(re.finditer(path_pattern, text))
        
        for match in matches:
            start, end = match.span()
            if start <= cursor_pos <= end:
                return match.group(), start, end
        
        # If no path pattern found, check if we're at the end of a word that could be a filename
        word_pattern = r'\S*'
        word_match = re.search(r'\S*$', text[:cursor_pos])
        if word_match:
            word = word_match.group()
            if '.' in word or word.startswith(('.', '/', '~')):
                start = cursor_pos - len(word)
                return word, start, cursor_pos
                
        return None, 0, 0
    
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        
        # Handle command completions (starts with / or !)
        if text.startswith('/'):
            # If there's a space, handle sub-commands
            if ' ' in text:
                if text.startswith('/provider '):
                    partial = text[10:]  # Remove '/provider '
                    for provider in ['openai', 'claude']:
                        if provider.startswith(partial):
                            yield Completion(provider, start_position=-len(partial))
                elif text.startswith('/role '):
                    partial = text[6:]  # Remove '/role '
                    for role in ['tutor', 'simple']:
                        if role.startswith(partial):
                            yield Completion(role, start_position=-len(partial))
                elif text.startswith('/ask '):
                    # For /ask, provide file path completions after the command
                    # Extract the part after '/ask '
                    ask_content = text[5:]  # Remove '/ask '
                    # Create a sub-document for path completion
                    from prompt_toolkit.document import Document
                    path_document = Document(ask_content, len(ask_content))
                    # Get path completions
                    for completion in self.path_completer.get_completions(path_document, complete_event):
                        yield completion
                elif text.startswith('/prompt '):
                    # For /prompt, provide file path completions after the command
                    # Extract the part after '/prompt '
                    prompt_content = text[8:]  # Remove '/prompt '
                    # Create a sub-document for path completion
                    from prompt_toolkit.document import Document
                    path_document = Document(prompt_content, len(prompt_content))
                    # Get path completions
                    for completion in self.path_completer.get_completions(path_document, complete_event):
                        yield completion
            else:
                # Complete main commands
                for command in self.commands:
                    if command.startswith(text):
                        yield Completion(command, start_position=-len(text))
        
        elif text.startswith('!'):
            # For bash commands, provide file path completions after the command
            if ' ' in text:
                # Extract the part after the command for path completion
                parts = text.split(' ', 1)
                if len(parts) > 1:
                    path_part = parts[1]
                    # Create a sub-document for path completion
                    from prompt_toolkit.document import Document
                    path_document = Document(path_part, len(path_part))
                    # Get path completions
                    for completion in self.path_completer.get_completions(path_document, complete_event):
                        yield completion
        
        else:
            # For regular text, only provide file completions if we detect a path-like pattern at cursor
            path, start_pos, end_pos = self._extract_path_at_cursor(text, len(text))
            if path:
                # Use custom file completion logic
                import os
                import glob
                
                try:
                    # Handle different path patterns
                    if path.startswith('~/'):
                        # Expand home directory
                        expanded_path = os.path.expanduser(path)
                        search_pattern = expanded_path + '*'
                    elif path.startswith('./') or path.startswith('../') or path.startswith('/'):
                        # Relative or absolute paths
                        search_pattern = path + '*'
                    else:
                        # Plain filename - search in current directory
                        search_pattern = path + '*'
                    
                    # Get matching files and directories
                    matches = glob.glob(search_pattern)
                    
                    for match in matches:
                        # Get just the filename part for display
                        if path.startswith('~/'):
                            # For home directory paths, show the ~/... format
                            completion_text = '~/' + os.path.relpath(match, os.path.expanduser('~'))
                        elif os.path.dirname(path):
                            # For paths with directories, preserve the directory part
                            completion_text = match
                        else:
                            # For plain filenames, show just the filename
                            completion_text = os.path.basename(match)
                        
                        # Add trailing slash for directories
                        if os.path.isdir(match):
                            completion_text += '/'
                        
                        # Calculate the start position to replace the entire path part
                        start_position = start_pos - len(text)
                        yield Completion(completion_text, start_position=start_position)
                        
                except (OSError, ValueError):
                    # If there's an error with file system access, don't provide completions
                    pass

class TerminalInterface:
    def __init__(self):
        self.console = Console()
        self.last_ctrl_c_time = 0
        self.command_completer = CommandCompleter()
        
    def show_welcome(self):
        """Display welcome message"""
        welcome_text = """
🤖 AI Programming Tutor

Welcome to your AI pair programming partner!

How to Use:
• Type messages to the tutor
• Press Enter to submit, Alt+Enter for new lines
• Type /help to see all available commands
• Press Tab for command and file/folder autocomplete
• Use !<command> for bash commands (e.g., !ls)

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
                    # Regular text - render as markdown
                    if part.strip():
                        markdown_content = Markdown(part.strip())
                        text_panel = Panel(
                            markdown_content,
                            border_style="cyan",
                            padding=(0, 2)
                        )
                        self.console.print(text_panel)
        else:
            # Single part (no code blocks) - render as markdown
            markdown_content = Markdown(content)
            response_panel = Panel(
                markdown_content,
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
        
        help_table.add_row("Direct messaging", "Just type your message and press Enter to submit")
        help_table.add_row("Multi-line input", "Press Alt+Enter for new lines, Enter to submit")
        help_table.add_row("!<command>", "Execute bash command (e.g., !ls, !git status)")
        help_table.add_row("/ask <question>", "Ask a direct question (uses simple tutor, not Socratic)")
        help_table.add_row("/prompt <text>", "Send completely raw prompt (no system prompt)")
        help_table.add_row("/provider <name>", "Switch AI provider (openai, claude)")
        help_table.add_row("/config", "Show current configuration")
        help_table.add_row("/log", "View conversation history")
        help_table.add_row("/log save", "Save conversation history to file")
        help_table.add_row("/resume", "List available conversation logs to resume")
        help_table.add_row("/resume <filename>", "Resume conversation from log file")
        help_table.add_row("/resume latest", "Resume from auto-saved latest conversation")
        help_table.add_row("/role tutor", "Switch to Socratic tutor mode")
        help_table.add_row("/role simple", "Switch to simple tutor mode")
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
        
        @bindings.add('enter')
        def _(event):
            """Handle Enter - submit the message"""
            event.app.exit(result=event.app.current_buffer.text)
        
        @bindings.add('escape', 'enter')  # Alt+Enter
        def _(event):
            """Handle Alt+Enter - insert new line"""
            event.app.current_buffer.insert_text('\n')
        
        try:
            # Use custom key bindings: Enter submits, Alt+Enter adds new lines
            result = prompt(
                prompt_text,
                wrap_lines=True,
                key_bindings=bindings,
                completer=self.command_completer
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
