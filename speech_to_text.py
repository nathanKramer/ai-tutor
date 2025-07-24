import speech_recognition as sr
import pyaudio
import os
import warnings
from typing import Optional

# Suppress ALSA warnings
os.environ['ALSA_PCM_CARD'] = 'default'
os.environ['ALSA_PCM_DEVICE'] = '0'
warnings.filterwarnings("ignore", category=UserWarning)

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

    def listen_continuously(self, debug: bool = False) -> Optional[str]:
        """
        Continuously listen for speech and convert to text

        Args:
            debug: Print debug information

        Returns:
            Recognized text or None if no speech detected/understood
        """
        if not self.microphone:
            if debug:
                print("❌ No microphone available")
            return None

        try:
            if debug:
                print("🎤 Waiting for speech...")

            with self.microphone as source:
                # Reduce timeout and be more aggressive about detecting speech
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)

            if debug:
                print("🔄 Processing audio...")

            text = self.recognizer.recognize_google(audio)

            if debug:
                print(f"✅ Recognized: '{text}'")

            return text

        except sr.WaitTimeoutError:
            if debug:
                print("⏰ No speech detected - continuing to listen...")
            return None
        except sr.UnknownValueError:
            if debug:
                print("❓ Could not understand audio - continuing...")
            return None  # Could not understand audio - keep listening
        except sr.RequestError as e:
            print(f"❌ Error with speech recognition service: {e}")
            return None
        except Exception as e:
            if debug:
                print(f"❌ Unexpected error in speech recognition: {e}")
            return None

    def is_microphone_available(self) -> bool:
        """Check if microphone is available"""
        return self.microphone is not None
