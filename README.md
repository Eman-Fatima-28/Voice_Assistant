Voice-Controlled Task Automation System
A comprehensive Jarvis-like voice assistant for Windows that automates repetitive tasks through natural language commands.

Contents:
- Overview
- Features
- System Requirements
- Installation
- Configuration
- Usage
- Adding New Commands
- Troubleshooting
- Known Limitations
- License


Overview
This voice-controlled automation system enables users to perform daily computer tasks through natural language voice commands. Built with Python, it provides hands-free control over applications, files, system information, and more—improving productivity by minimizing repetitive manual operations.
Key Highlights:

Natural language processing for flexible command interpretation
Modular architecture for easy extensibility
Offline text-to-speech feedback
Cross-platform support (optimized for Windows)


Features
Application Control

Launch applications (Notepad, Excel, VS Code, Chrome, etc.)
Close running applications
Flexible command variations supported

Web & Information

Open websites (Gmail, YouTube, Google, GitHub)
Perform web searches via Google
Retrieve current weather information (OpenWeatherMap API)
Get latest news headlines (NewsAPI)

File & Folder Management

Create dated project folders automatically
Create regular folders with custom names
Organize Downloads folder by file type
Search for files across the system
Capture screenshots
Rename files and folders

Media Playback

Play local music from Music folder
Play YouTube videos/songs via voice command

System Information

Query current time and date
Get weather reports for any city
Retrieve latest news by category

System Controls

Screen brightness adjustment (up, down, set level)
Wi-Fi connectivity toggle (Windows only)
Screenshot capture with automatic timestamping

Window & UI Automation

Switch between open windows
Scroll pages up and down
Type dictated text in active window

Email Management (Optional - Requires Gmail configuration)

Send emails with multi-step voice composition
Read recent email subjects from inbox


System Requirements
Minimum Specifications
ComponentMinimumRecommendedProcessorIntel i3 (6th gen) or AMD equivalentIntel i5 (8th gen) or AMD Ryzen 5RAM4 GB8 GBStorage500 MB free space1 GB free spaceOperating SystemWindows 10 (64-bit)Windows 11Internet2 Mbps (for voice recognition)Broadband connection (10+ Mbps)MicrophoneAny USB or built-in microphoneNoise-canceling USB microphoneAudio OutputSpeakers or headphonesAny audio device

Platform Support
PlatformStatusNotesWindows 10/11Fully SupportedPrimary development platformmacOSPartial SupportSome features unavailableLinuxPartial SupportLimited system automation

Why These Requirements?

RAM: Speech recognition libraries and TTS engines require significant memory (~2 GB during operation)
Processor: Real-time audio processing demands adequate CPU resources
Internet: Google Speech Recognition API requires active internet connection
Microphone: Quality directly impacts recognition accuracy


Installation
Step 1: Install Python

Download Python 3.10 or higher from python.org
During installation, check the box for "Add Python to PATH"
Verify installation:

bash   python --version
Step 2: Download Project
Option A: Clone Repository
bashgit clone <repository-url>
cd voice-assistant
Option B: Download ZIP

Download and extract the project ZIP file
Navigate to the extracted folder

Step 3: Install Dependencies
bash# Install all required packages
pip install -r requirements.txt

# If errors occur, upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt
Step 4: Install PyAudio (Special Handling)
PyAudio installation can be challenging on Windows.
Windows:
bash# Method 1: Using pipwin
pip install pipwin
pipwin install pyaudio

# Method 2: Download precompiled wheel
# Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Download appropriate wheel for your Python version
# Install: pip install <downloaded_wheel_file.whl>
macOS:
bashbrew install portaudio
pip install pyaudio
Linux:
bashsudo apt-get install python3-pyaudio
pip install pyaudio
Step 5: Test Microphone
Verify microphone access and functionality:
bashpython -c "from modules.voice_recognizer import VoiceRecognizer; VoiceRecognizer().test_microphone()"

Configuration
1. Create Environment Configuration File
Create a file named .env in the project root directory:
env# Email Configuration (Optional - for email features)
SENDER_EMAIL=your.email@gmail.com
SENDER_PASSWORD=your_app_password_here

# API Keys (Optional - for weather/news features)
WEATHER_API_KEY=your_openweather_api_key
NEWS_API_KEY=your_newsapi_key

# Default Settings
DEFAULT_CITY=London
DEFAULT_NEWS_CATEGORY=technology
2. Obtain API Keys (Optional but Recommended)
Gmail App Password (for email features)

Visit Google Account Security
Enable 2-Factor Authentication
Go to App Passwords
Select "Mail" and your device type
Generate password (16 characters)
Copy to .env file

Important: Use App Password, not your regular Gmail password.
OpenWeatherMap API (for weather features)

Sign up at OpenWeatherMap
Free tier: 1,000 API calls per day
Copy API key from dashboard
Paste in .env file

NewsAPI (for news features)

Register at NewsAPI
Free tier: 100 requests per day
Copy API key from account page
Paste in .env file

3. Verify Configuration
bashpython -c "from config import Config; Config.validate()"
This command displays which features are enabled or disabled based on your configuration.

Usage
Starting the Assistant
bashpython main.py
```

### Expected Output
```
============================================================
  VOICE-CONTROLLED TASK AUTOMATION SYSTEM
============================================================

Configuration Status:
All features configured and ready!

Say commands like:
   - 'Open Notepad'
   - 'What's the time?'
   - 'Create folder reports'
   - 'Take a screenshot'
   - 'Search for presentation files'
   - 'Play music'
   - 'Exit' to quit

============================================================

Voice assistant started. How can I help you?
Listening...
```

### Stopping the Assistant

- Say **"Exit"** or **"Quit"**
- Press **Ctrl+C**

### Usage Examples

#### Example 1: Application Control
```
User: "Open Notepad"
Assistant: "Opening Notepad."
[Notepad window opens]

User: "Close Notepad"
Assistant: "Closed Notepad."
```

#### Example 2: Folder Management
```
User: "Create project folder Sales Report"
Assistant: "Folder created: Sales_Report_2026-01-25"

User: "Create folder Documents"
Assistant: "Folder created: Documents"
```

#### Example 3: System Information
```
User: "What's the time?"
Assistant: "The time is 3:45 PM."

User: "Weather in New York"
Assistant: "In New York, it's 5°C with clear skies."
```

#### Example 4: File Operations
```
User: "Search for presentation files"
Assistant: "Found 8 files. Showing first few."
[File paths displayed in console]

User: "Take a screenshot"
Assistant: "Screenshot saved."
```

#### Example 5: Email Workflow
```
User: "Send email"
Assistant: "Who should I send this to?"
User: "manager@company.com"
Assistant: "What's the subject?"
User: "Weekly Report"
Assistant: "What's the message?"
User: "The report is ready for review"
Assistant: "Ready to send. Say yes to send, or no to cancel."
User: "Yes"
Assistant: "Email sent to manager@company.com"
For a complete list of voice commands, refer to COMMANDS_REFERENCE.md.

Adding New Commands
Method 1: Simple Command (No Parameters)
Step 1: Add command recognition in modules/command_mapper.py
pythondef normalize(self, command: str):
    # Existing code...
    
    # Add new command detection
    if 'shutdown' in command and 'computer' in command:
        return ('shutdown_computer', None, None)
Step 2: Add action handler in modules/command_processor.py
pythondef process_command(command: str) -> bool:
    # Existing code...
    
    elif action == 'shutdown_computer':
        os.system('shutdown /s /t 10')
        tts.speak_success("Shutting down computer in 10 seconds.")
Method 2: Command with Parameters
Step 1: Add to modules/action_executor.py
pythondef custom_action(self, *, param: str, timestamp: Optional[float] = None) -> ExecResult:
    """Execute custom action"""
    ts = timestamp or _now_ts()
    
    try:
        # Your implementation
        result = perform_task(param)
        
        return ExecResult(
            ok=True,
            message="Task completed successfully",
            action="custom_action",
            data={"result": result},
            timestamp=ts
        )
    
    except Exception as e:
        return ExecResult(
            ok=False,
            message="Task failed",
            action="custom_action",
            error=str(e),
            timestamp=ts
        )
Step 2: Register in action dispatcher
pythonaction_map = {
    # Existing actions...
    'custom_action': lambda: self.custom_action(
        param=kwargs.get('param'),
        timestamp=ts
    ),
}
Step 3: Add command processing logic
pythonelif action == 'custom_action':
    param = parameter or target
    if param:
        res = executor.execute("custom_action", param=param)
        tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)

Troubleshooting
Microphone Issues
Problem: "Microphone error" or no audio capture
Solutions:

Verify microphone is properly connected
Enable microphone permissions in Windows Settings → Privacy → Microphone
Test microphone:

bash   python -c "from modules.voice_recognizer import VoiceRecognizer; VoiceRecognizer().test_microphone()"

Try a different USB port or microphone

Speech Recognition Issues
Problem: "Speech recognition service unavailable"
Solutions:

Verify internet connection (ping google.com)
Check if firewall is blocking Python
Upgrade speech recognition library:

bash   pip install --upgrade SpeechRecognition
Text-to-Speech Issues
Problem: "pyttsx3 init failed" or no audio output
Solutions:

Reinstall pyttsx3:

bash   pip uninstall pyttsx3
   pip install pyttsx3==2.90

Verify audio output device is connected
Check system audio settings

Command Recognition Issues
Problem: Commands not recognized or misunderstood
Solutions:

Speak clearly and at moderate pace
Reduce background noise
Use command variations (e.g., "open notepad" vs "launch notepad")
Check COMMANDS_REFERENCE.md for exact phrasing
Review console output for debug information

Application Launch Issues
Problem: "Unable to open application"
Solutions:

Verify application is installed on the system
Check application paths in action_executor.py app_map
For Microsoft Office apps, verify installation path:

Common paths: C:\Program Files\Microsoft Office\root\Office16\


Add custom application paths to app_map dictionary

Email Issues
Problem: Email authentication failed or emails not sending
Solutions:

Verify .env file contains correct Gmail credentials
Use Gmail App Password (not regular password)

Get from: https://myaccount.google.com/apppasswords


Enable 2-Factor Authentication on Google Account
Test configuration:

bash   python -c "from config import Config; print(Config.SENDER_EMAIL)"
Brightness Control Issues
Problem: "Brightness control not available"
Solution:
bashpip install screen-brightness-control
```

---

## Known Limitations

### Environmental Constraints

- **Background Noise:** High ambient noise significantly reduces recognition accuracy
- **Accent Sensitivity:** Google Speech API may have difficulty with strong regional accents
- **Internet Dependency:** Voice recognition requires active internet connection (2+ Mbps)
- **Speech Overlap:** Cannot process commands while assistant is speaking

### Platform Limitations

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| **Application Control** | Full Support | Limited | Limited |
| **Brightness Control** | Full Support | Full Support | Limited |
| **Wi-Fi Toggle** | Supported | Not Supported | Not Supported |
| **File Operations** | Full Support | Full Support | Full Support |
| **Screenshots** | Full Support | Full Support | Full Support |

### Functional Limitations

- **Single Command Processing:** Cannot execute multiple commands simultaneously (e.g., "Open Notepad and Excel")
- **Command History:** No ability to repeat previous commands
- **File Search Depth:** Limited to first 20 results
- **Screenshot Region:** Only full-screen capture supported
- **Email Provider:** Gmail only (SMTP/IMAP hardcoded)
- **Multi-language:** English commands only

### Performance Considerations

- **Initial Delay:** First command may take 3-5 seconds due to engine initialization
- **Recognition Latency:** 1-2 second delay for Google API processing
- **CPU Usage:** 20-40% during active listening (normal behavior)
- **Memory Footprint:** Approximately 2 GB RAM usage during operation

### Security Considerations

- **Credential Storage:** API keys stored in plaintext `.env` file (local only)
- **Access Control:** No user authentication mechanism
- **File Operations:** Restricted to predefined safe directories
- **Email Security:** Requires App Password instead of main password
- **Audit Trail:** No command execution logging by default

---

## License

This project is developed for educational and productivity purposes.

---

## Credits

- **Speech Recognition:** Google Speech API
- **Text-to-Speech:** pyttsx3 (offline engine)
- **Weather Data:** OpenWeatherMap API
- **News Data:** NewsAPI
- **Brightness Control:** screen-brightness-control library

---

## Project Structure
```
voice-assistant/
├── main.py                      # Main entry point
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables (create this)
├── README.md                    # This file
├── modules/
│   ├── __init__.py
│   ├── voice_recognizer.py     # Voice input handling
│   ├── command_processor.py    # Command routing
│   ├── command_mapper.py       # Natural language parsing
│   ├── action_executor.py      # System automation
│   └── tts_engine.py          # Text-to-speech feedback

For detailed command reference, see COMMAND_REFERENCE.pdf
For step-by-step setup instructions, see DOCUMENTATION(INSTRUCTIONS).pdf