# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered pair programming tutor that provides text-based interaction for coding assistance. The system supports multiple AI providers (OpenAI GPT and Anthropic Claude) and creates a conversational programming assistant through a terminal interface.

## Architecture

The application follows a modular architecture with clear separation of concerns:

- **main.py**: Main application entry point and orchestration
- **ai_tutor.py**: Multi-provider AI integration and conversation management
- **terminal_interface.py**: Rich-based terminal UI components
- **config.py**: Configuration management for AI provider selection

The main application (`AIPairProgrammingTutor`) coordinates between these components, handling text input and commands in the main loop.

## Setup and Dependencies

**Environment Setup:**
```bash
# Setup script handles virtual environment and dependencies
./setup.sh

# Manual setup
source venv/bin/activate
pip install -r requirements.txt
```

**Required Environment Variables (at least one):**
- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude models

**System Requirements:**
- Python 3.x with virtual environment

## Running the Application

**Primary command:**
```bash
source venv/bin/activate
python3 main.py
```

**Debug mode:**
```bash
python3 main.py --debug
```

**Help:**
```bash
python3 main.py --help
```

## Key Components

**AI Integration**: Supports multiple AI providers:
- **OpenAI**: GPT models (default: gpt-3.5-turbo)
- **Claude**: Anthropic models (default: claude-3-haiku-20240307)

Features conversation history management (configurable limit) and context-aware responses based on current directory code files.

**Text Interface**: Terminal-based interaction using Rich library for formatted output and user input handling.

**Error Handling**: Graceful degradation when components fail - the application continues running with reduced functionality if AI components are unavailable.

## Development Notes

The application provides a text-based interface for interacting with the AI tutor. Users can:
- Type messages directly (no command needed)
- Use slash commands for system functions (e.g., /help, /quit)
- Switch between AI providers using '/provider <name>'
- View configuration with '/config' command
- Multi-line input supported with Shift+Enter

The AI tutor maintains conversation context and incorporates information about the current working directory and code files.

## AI Provider Configuration

**Default Configuration:**
- Provider: OpenAI (can be switched to Claude)
- Models: gpt-3.5-turbo (OpenAI), claude-3-haiku-20240307 (Claude)
- Max tokens: 200
- Temperature: 0.7
- Conversation history limit: 10 messages

**Switching Providers:**
```bash
# Switch to Claude
/provider claude

# Switch to OpenAI
/provider openai

# Show current configuration
/config
```

**Configuration File:**
Settings are automatically saved to `tutor_config.json` and can be manually edited.

No testing framework is currently implemented in this codebase.

## Supported AI Models

**OpenAI Models:**
- gpt-3.5-turbo (default)
- gpt-4
- Other OpenAI chat models

**Claude Models:**
- claude-3-haiku-20240307 (default)
- claude-3-sonnet-20240229
- claude-3-opus-20240229
- Other Anthropic models

Models can be configured in the `tutor_config.json` file.