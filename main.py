"""
Voice-Controlled Repetitive Task Automation System
Main entry point with error handling and graceful shutdown
"""

import sys
import signal
from modules.voice_recognizer import VoiceRecognizer
from modules.command_processor import process_command
from modules.tts_engine import TTSFeedbackEngine
from config import Config, config_warnings


# Global instances
recognizer = VoiceRecognizer()
tts = TTSFeedbackEngine()


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n⚠️  Shutdown signal received...")
    tts.speak_success("Voice assistant stopped by user.")
    tts.shutdown()
    sys.exit(0)


def main():
    """Main application loop"""
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Display startup banner
    print("\n" + "="*60)
    print("  🎙️  VOICE-CONTROLLED TASK AUTOMATION SYSTEM")
    print("="*60)
    print("\n📋 Configuration Status:")
    
    if config_warnings:
        for warning in config_warnings:
            print(warning)
    else:
        print("✅ All features configured and ready!")
    
    print("\n💡 Say commands like:")
    print("   • 'Open Notepad'")
    print("   • 'What's the time?'")
    print("   • 'Create folder reports'")
    print("   • 'Take a screenshot'")
    print("   • 'Search for presentation files'")
    print("   • 'Play music'")
    print("   • 'Exit' to quit")
    print("\n" + "="*60 + "\n")
    
    try:
        # Welcome message
        tts.speak_success("Voice assistant started. How can I help you?")
        
        running = True
        error_count = 0
        max_consecutive_errors = 5
        
        while running:
            try:
                # Listen for command
                command = recognizer.listen()
                
                if command:
                    print(f"📝 Processing: {command}")
                    
                    # Process command
                    running = process_command(command)
                    
                    # Reset error count on successful command
                    error_count = 0
                
                else:
                    # No command recognized (already provided feedback in recognizer)
                    error_count += 1
                    
                    if error_count >= max_consecutive_errors:
                        print(f"\n⚠️  Too many consecutive errors ({error_count})")
                        tts.speak_warning("I'm having trouble hearing you. Please check your microphone.")
                        error_count = 0  # Reset after warning
            
            except KeyboardInterrupt:
                # Ctrl+C pressed
                print("\n\n⚠️  Keyboard interrupt detected...")
                tts.speak_success("Voice assistant stopped.")
                running = False
            
            except Exception as e:
                # Unexpected error during command processing
                print(f"❌ Error processing command: {e}")
                tts.speak_error("An error occurred. Please try again.")
                error_count += 1
                
                if error_count >= max_consecutive_errors:
                    print(f"\n❌ Critical: Too many errors. Shutting down.")
                    tts.speak_error("Critical error. Shutting down.")
                    running = False
    
    except Exception as e:
        # Fatal error during initialization or main loop
        print(f"\n❌ Fatal error: {e}")
        tts.speak_error("Critical error. Voice assistant shutting down.")
    
    finally:
        # Cleanup
        print("\n🔄 Cleaning up...")
        tts.shutdown()
        print("✅ Voice assistant stopped.\n")


if __name__ == "__main__":
    main()