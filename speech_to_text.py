import speech_recognition as sr
import pyaudio
import os
import warnings
from typing import Optional

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None

        # Try to find a working microphone
        self._initialize_microphone()

    def _initialize_microphone(self):
        """Initialize microphone with fallback options"""
        try:
            # Try default microphone first
            self.microphone = sr.Microphone()

            # Test if it works and adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

            print("✅ Microphone initialized successfully")

        except Exception as e:
            print(f"⚠️  Default microphone failed: {e}")

            # Try to find alternative microphones
            try:
                mic_list = sr.Microphone.list_microphone_names()
                print(f"Available microphones: {len(mic_list)}")

                for i, mic_name in enumerate(mic_list):
                    try:
                        test_mic = sr.Microphone(device_index=i)
                        with test_mic as source:
                            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                        self.microphone = test_mic
                        print(f"✅ Using microphone {i}: {mic_name}")
                        break

                    except Exception:
                        continue

                if not self.microphone:
                    print("❌ No working microphone found")

            except Exception as e:
                print(f"❌ Could not initialize any microphone: {e}")

    def listen_continuously(self) -> Optional[str]:
        """
        Continuously listen for speech and convert to text

        Returns:
            Recognized text or None if no speech detected/understood
        """
        if not self.microphone:
            print("❌ No microphone available")
            return None

        try:
            print("🎤 Waiting for speech...")

            with self.microphone as source:
                # Increased timeout for better user experience
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=15)

            print("🔄 Processing audio...")

            text = self.recognizer.recognize_google(audio)

            print(f"✅ Recognized: '{text}'")

            return text

        except sr.WaitTimeoutError:
            print("⏰ No speech detected - continuing to listen...")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand audio - try speaking more clearly")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition service error: {e}")
            print("💡 Check your internet connection")
            return None
        except Exception as e:
            print(f"❌ Unexpected error in speech recognition: {e}")
            return None

    def is_microphone_available(self) -> bool:
        """Check if microphone is available"""
        return self.microphone is not None
