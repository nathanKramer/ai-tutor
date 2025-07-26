# AI Programming Tutor

**Note**: This project is a vibe-coded CLI agent that is "throw away" code at the moment.

<img width="800" height="482" alt="Screenshot From 2025-07-26 16-46-14" src="https://github.com/user-attachments/assets/6a78f7e7-0f43-44db-b241-9a946701fee6" />

Currently supports anthropic and openai, basic tool calling (list files / read files), several different system prompts, abilitiy to resume conversations after closing, and more.

## Installation

### Prerequisites
- Python 3
- At least one API key:
  - OpenAI API key for GPT models
  - Anthropic API key for Claude models

### Setup
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-tutor
   ```

2. **Run the setup script**:
   ```bash
   ./build.sh
   ```
   This will build the binary to the `dist` folder.

3. **Set up API keys**:
   ```bash
   # For OpenAI (choose one):
   export OPENAI_API_KEY="your-openai-api-key"
   
   # For Anthropic Claude (choose one):
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   ```

4. **Run the tutor**:
   ```bash
   ./dist/ai
   ```

### Running with python

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 main.py
```

## Usage

### Basic Interaction
- **Ask questions**: Simply type your question and press Enter
- **Multi-line input**: Use Alt+Enter for new lines
- **Get help**: Type `/help` for all available commands

### Commands

#### Core Commands
- `/help` - Show all available commands
- `/quit` or `/exit` - End the session
- `/clear` - Clear conversation history and screen

#### AI Provider Management
- `/provider openai` - Switch to OpenAI GPT
- `/provider claude` - Switch to Anthropic Claude
- `/config` - Show current configuration

#### Interaction Modes
- `/role tutor` - Switch to Socratic tutor mode (default)
- `/role simple` - Switch to direct answer mode
- `/role short` - Switch to brief response mode

#### Question Types
- `<message>` - Regular conversation (uses current role)
- `/ask <question>` - Direct question (uses simple mode)
- `/prompt <text>` - Raw prompt with no system instructions

#### Conversation Management
- `/log` - View current conversation history
- `/log save` - Save conversation to timestamped file
- `/resume` - List available conversation logs
- `/resume <filename>` - Resume from specific log file
- `/resume latest` - Resume from auto-saved conversation

#### Utilities
- `/copy` - Copy last AI response to clipboard
- `!<command>` - Execute bash commands (e.g., `!ls`, `!git status`)

### Configuration

The application stores configuration in `~/.config/ai-tutor/`:
- `tutor_config.json` - User preferences and settings
- `latest.jsonl` - Auto-saved conversation log  
- `ai_tutor.log` - Application logs
- `conversation_log_*.jsonl` - Manual conversation saves

### Examples

```bash
# Start a coding session
> How do I implement a binary search in Python?

# Switch to brief responses
> /role short

# Ask a direct question
> /ask What's the time complexity of quicksort?

# Execute a command
> !python my_script.py

# Copy the AI's response
> /copy

# Save and resume conversations
> /log save
> /resume latest
```

## Building for Distribution

Create a standalone executable that doesn't require Python:

```bash
# Quick build
./build.sh

# Create full release package
./release.sh
```

The build process creates:
- `ai` - Standalone executable (~50MB)
- `README.txt` - User documentation
- Installation scripts
- Compressed archive for distribution

## Architecture

### Core Components
- **main.py**: Application orchestration and command handling
- **ai_tutor.py**: Multi-provider AI integration
- **terminal_interface.py**: Rich-based UI components
- **config.py**: Configuration management

### Provider System
- **providers/**: AI provider implementations
- **ProviderFactory**: Dynamic provider creation
- **Extensible**: Easy to add new AI providers

### Prompt Management
- **core/prompt_manager.py**: System prompt handling
- **prompts/**: Modular prompt files
- **Role-based**: Different prompts for different interaction modes

## Requirements

### Core Dependencies
- `rich` - Rich terminal interface
- `prompt_toolkit` - Advanced input handling
- `python-dotenv` - Environment variable management

### AI Provider Dependencies
- `openai` - OpenAI GPT integration
- `anthropic` - Claude integration

### Optional Dependencies
- `pyperclip` - Clipboard functionality (falls back to system commands)

## Configuration Options

The `tutor_config.json` file supports:

```json
{
  "ai_provider": "openai",
  "models": {
    "openai": "gpt-3.5-turbo",
    "claude": "claude-sonnet-4-20250514"  
  },
  "role": "tutor",
  "max_tokens": 1000,
  "temperature": 0.7,
  "conversation_history_limit": 10
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the existing code style
4. Test thoroughly with both AI providers
5. Submit a pull request

## License

MIT License.

## Support

For issues and feature requests, please use the project's issue tracker.
