"""
Voice Recognition Module with Error Handling and User Feedback
"""

import speech_recognition as sr
from config import Config


class VoiceRecognizer:
    """Handles voice input with robust error handling and user feedback."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Lower = more sensitive
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5

        # Import TTS here to avoid circular dependency
        from modules.tts_engine import TTSFeedbackEngine
        self.tts = TTSFeedbackEngine()

    def listen(self, timeout=None, phrase_time_limit=None):
        """
        Listen for a voice command with error handling and debug info.

        Args:
            timeout (float): Max seconds to wait for speech (defaults to Config.RECOGNITION_TIMEOUT)
            phrase_time_limit (float): Max seconds for a single phrase (defaults to Config.PHRASE_TIME_LIMIT)

        Returns:
            str: Recognized command text (lowercase, stripped)
            None: If no command is recognized
        """
        timeout = timeout or Config.RECOGNITION_TIMEOUT
        phrase_time_limit = phrase_time_limit or Config.PHRASE_TIME_LIMIT

        try:
            with sr.Microphone() as source:
                print("🎤 Listening...")
                print(f"   ⏱️  Timeout: {timeout}s, Max phrase: {phrase_time_limit}s")
                print("   🔊 Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print(f"   📊 Energy threshold: {self.recognizer.energy_threshold}")
                print("   🗣️  Speak now!")

                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

                print("   ✅ Audio captured, recognizing...")

        except sr.WaitTimeoutError:
            print("   ⏰ Timeout - no speech detected")
            self.tts.speak_warning("I didn't hear anything. Please try again.")
            return None

        except Exception as e:
            print(f"   ❌ Microphone error: {e}")
            self.tts.speak_error("Microphone error. Please check your device.")
            return None

        # Recognize speech
        try:
            command = self.recognizer.recognize_google(audio)
            print(f"   ✅ Recognized: '{command}'")
            return command.lower().strip()

        except sr.UnknownValueError:
            print("   ❓ Could not understand audio")
            self.tts.speak_warning("Sorry, I didn't understand. Please repeat.")
            return None

        except sr.RequestError as e:
            print(f"   🌐 Recognition service error: {e}")
            self.tts.speak_error(
                "Speech recognition service unavailable. Check your internet connection."
            )
            return None

        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            self.tts.speak_error("An error occurred. Please try again.")
            return None

    def test_microphone(self):
        """Test if the microphone is working properly."""
        try:
            with sr.Microphone() as source:
                print("🎤 Testing microphone... Speak now!")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5)

                text = self.recognizer.recognize_google(audio)
                print(f"✅ Microphone test successful! Heard: {text}")
                return True

        except sr.WaitTimeoutError:
            print("⚠️  No speech detected during test")
            return False

        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return False


# Demo
if __name__ == "__main__":
    recognizer = VoiceRecognizer()

    print("\n=== Microphone Test ===")
    recognizer.test_microphone()

    print("\n=== Voice Recognition Demo ===")
    print("Speak a command...")

    command = recognizer.listen()
    if command:
        print(f"Command received: {command}")
    else:
        print("No command received")
