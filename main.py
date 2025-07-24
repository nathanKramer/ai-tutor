#!/usr/bin/env python3

import os
import sys
import threading
import time
from speech_to_text import SpeechToText
from text_to_speech import TextToSpeech
from ai_tutor import AITutor
from terminal_interface import TerminalInterface

class AIPairProgrammingTutor:
    def __init__(self, debug: bool = False):
        self.ui = TerminalInterface()
        self.stt = None
        self.tts = None
        self.ai_tutor = None
        self.running = False
        self.voice_mode = True
        self.debug = debug

        # Initialize components
        self._init_components()

    def _init_components(self):
        """Initialize all system components"""
        try:
            self.stt = SpeechToText()
            self.ui.show_success("Speech-to-Text initialized")
        except Exception as e:
            self.ui.show_error(f"Failed to initialize Speech-to-Text: {e}")

        try:
            self.tts = TextToSpeech()
            self.ui.show_success("Text-to-Speech initialized")
        except Exception as e:
            self.ui.show_error(f"Failed to initialize Text-to-Speech: {e}")

        try:
            self.ai_tutor = AITutor()
            self.ui.show_success("AI Tutor initialized")
        except Exception as e:
            self.ui.show_error(f"Failed to initialize AI Tutor: {e}")

    def continuous_voice_listener(self):
        """Continuously listen for voice input in background thread"""
        while self.running:
            if not self.stt:
                time.sleep(1)
                continue

            try:
                user_speech = self.stt.listen_continuously(debug=self.debug)

                if user_speech and user_speech.strip():
                    self.ui.show_user_input(user_speech)
                    self.process_user_input(user_speech)

            except Exception as e:
                self.ui.show_error(f"Voice input error: {e}")
                time.sleep(1)

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

        # Display and speak the response
        self.ui.show_ai_response(ai_response)

        if self.tts and self.voice_mode:
            self.tts.speak(ai_response)

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

    def handle_text_command(self, command: str):
        """Handle text-based commands"""
        command = command.lower().strip()

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
                stt_available=self.stt is not None and self.stt.is_microphone_available(),
                tts_available=self.tts is not None,
                ai_available=self.ai_tutor is not None
            )

        elif command.startswith('say '):
            # Allow typing messages directly
            message = command[4:].strip()
            if message:
                self.process_user_input(message)

        elif command == 'voice toggle':
            self.voice_mode = not self.voice_mode
            status = "enabled" if self.voice_mode else "disabled"
            self.ui.show_info(f"Voice output {status}")

        else:
            self.ui.show_info("Unknown command. Type 'help' for available commands.")

    def start_voice_listener(self):
        """Start continuous voice listening in background thread"""
        if self.stt and self.stt.is_microphone_available():
            voice_thread = threading.Thread(target=self.continuous_voice_listener, daemon=True)
            voice_thread.start()
            self.ui.show_info("🎤 Continuous voice listening active")
        else:
            self.ui.show_error("Microphone not available - voice input disabled")

    def run(self):
        """Main application loop"""
        # self.ui.clear_screen()
        self.ui.show_welcome()

        # Check component availability
        self.ui.show_status(
            stt_available=self.stt is not None and self.stt.is_microphone_available(),
            tts_available=self.tts is not None,
            ai_available=self.ai_tutor is not None
        )

        # Start continuous voice listening
        self.start_voice_listener()

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

        if self.tts:
            self.tts.stop()

        # No keyboard cleanup needed anymore
        pass

def main():
    """Entry point"""
    debug = '--debug' in sys.argv

    if len(sys.argv) > 1 and '--help' in sys.argv:
        print("AI Pair Programming Tutor")
        print("\nUsage: python main.py [--debug] [--help]")
        print("\nOptions:")
        print("  --debug    Enable debug output for speech recognition")
        print("  --help     Show this help message")
        print("\nRequires:")
        print("- OpenAI API key in OPENAI_API_KEY environment variable")
        print("- Microphone access for speech input")
        print("- Audio output for speech synthesis")
        return

    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set.")
        print("   You can still use the tutor, but AI responses won't work.")
        print("   Set your API key with: export OPENAI_API_KEY='your-key-here'")
        input("Press Enter to continue anyway...")

    tutor = AIPairProgrammingTutor(debug=debug)
    tutor.run()

if __name__ == "__main__":
    main()
