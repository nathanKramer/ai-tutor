import pyttsx3
from typing import Dict, Any

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self._configure_voice()
    
    def _configure_voice(self):
        """Configure voice settings for better experience"""
        voices = self.engine.getProperty('voices')
        
        # Try to find a female voice for variety
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate (words per minute)
        self.engine.setProperty('rate', 180)
        
        # Set volume (0.0 to 1.0)
        self.engine.setProperty('volume', 0.9)
    
    def speak(self, text: str, wait: bool = True):
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            wait: Whether to wait for speech to complete before returning
        """
        if not text.strip():
            return
            
        print(f"🔊 AI Tutor: {text}")
        self.engine.say(text)
        
        if wait:
            self.engine.runAndWait()
    
    def speak_async(self, text: str):
        """Speak text without waiting for completion"""
        self.speak(text, wait=False)
    
    def stop(self):
        """Stop current speech"""
        self.engine.stop()
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get current voice configuration"""
        return {
            'rate': self.engine.getProperty('rate'),
            'volume': self.engine.getProperty('volume'),
            'voice': self.engine.getProperty('voice')
        }
    
    def set_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        self.engine.setProperty('volume', max(0.0, min(1.0, volume)))