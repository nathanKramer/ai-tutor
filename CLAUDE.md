# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered pair programming tutor that provides voice-based interaction for coding assistance. The system combines speech-to-text, OpenAI's GPT API, and text-to-speech to create a conversational programming assistant.

## Architecture

The application follows a modular architecture with clear separation of concerns:

- **main.py**: Main application entry point and orchestration
- **ai_tutor.py**: OpenAI API integration and conversation management
- **speech_to_text.py**: Speech recognition using Google's speech recognition
- **text_to_speech.py**: Speech synthesis using pyttsx3
- **terminal_interface.py**: Rich-based terminal UI components

The main application (`AIPairProgrammingTutor`) coordinates between these components, running voice input in a background thread while handling text commands in the main loop.

## Setup and Dependencies

**Environment Setup:**
```bash
# Setup script handles virtual environment and dependencies
./setup.sh

# Manual setup
source venv/bin/activate
pip install -r requirements.txt
```

**Required Environment Variables:**
- `OPENAI_API_KEY`: OpenAI API key for AI responses

**System Requirements:**
- Microphone access for speech input
- Audio output for speech synthesis
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

**AI Integration**: Uses OpenAI's gpt-3.5-turbo model with conversation history management (last 10 messages) and context-aware responses based on current directory code files.

**Voice Processing**: Continuous background listening with timeout handling and microphone fallback detection. Speech synthesis with configurable voice properties.

**Error Handling**: Graceful degradation when components fail - the application continues running with reduced functionality if speech or AI components are unavailable.

## Development Notes

The application provides both voice and text interfaces simultaneously. Voice input runs continuously in a background thread while text commands are processed in the main loop. The AI tutor maintains conversation context and incorporates information about the current working directory and code files.

No testing framework is currently implemented in this codebase.