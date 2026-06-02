# Voice-Controlled Task Automation System

A comprehensive **Jarvis-like voice assistant for Windows** that automates repetitive tasks using natural language voice commands. Built with Python, it enables hands-free system control, improving productivity and user experience.

---

## 📌 Contents

* Overview
* Features
* System Requirements
* Installation
* Configuration
* Usage
* Adding New Commands
* Troubleshooting
* Known Limitations
* License
* Project Structure

---

## 🧠 Overview

This voice-controlled automation system allows users to perform daily computer tasks using natural language voice commands.

It is designed with a **modular architecture**, making it easy to extend and maintain. The system uses speech recognition and text-to-speech to provide interactive voice feedback.

### Key Highlights

* Natural language command processing
* Modular and extensible architecture
* Offline text-to-speech feedback
* Optimized for Windows automation

---

## ⚙️ Features

### 🖥 Application Control

* Launch and close applications (Notepad, Excel, VS Code, Chrome, etc.)
* Flexible command variations supported

### 🌐 Web & Information

* Open websites (YouTube, Gmail, GitHub, Google)
* Perform Google searches
* Get weather updates (OpenWeatherMap API)
* Fetch latest news (NewsAPI)

### 📁 File & Folder Management

* Create project folders automatically
* Organize downloads by file type
* Search files across system
* Capture screenshots
* Rename files and folders

### 🎵 Media Playback

* Play local music
* Open YouTube videos via voice command

### 💻 System Information

* Get current time and date
* Weather reports for any city
* Latest news headlines

### ⚙ System Controls

* Adjust screen brightness
* Toggle Wi-Fi (Windows)
* Take screenshots with timestamps

### 🪟 Window Automation

* Switch between windows
* Scroll pages
* Type dictated text

### 📧 Email (Optional)

* Send emails via voice
* Read recent inbox emails
  *(Requires Gmail configuration)*

---

## 💻 System Requirements

### Minimum Requirements

* CPU: Intel i3 (6th Gen) or equivalent
* RAM: 4 GB
* Storage: 500 MB free space
* OS: Windows 10 (64-bit)
* Internet: 2 Mbps
* Microphone: Any working mic

### Recommended

* CPU: Intel i5 / Ryzen 5
* RAM: 8 GB
* OS: Windows 11
* Internet: 10+ Mbps
* Noise-canceling microphone

---

## 📦 Installation

### Step 1: Install Python

Download Python 3.10+ from https://python.org
Enable **Add to PATH** during installation.

Verify:

```bash
python --version
```

---

### Step 2: Clone Repository

```bash
git clone <repository-url>
cd voice-assistant
```

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Upgrade pip if needed:

```bash
pip install --upgrade pip
```

---

### Step 4: Install PyAudio (Windows Fix)

```bash
pip install pipwin
pipwin install pyaudio
```

Alternative: download wheel from
https://www.lfd.uci.edu/~gohlke/pythonlibs/

---

### Step 5: Test Microphone

```bash
python -c "from modules.voice_recognizer import VoiceRecognizer; VoiceRecognizer().test_microphone()"
```

---

## 🔐 Configuration

Create a `.env` file in the project root:

```env
SENDER_EMAIL=your.email@gmail.com
SENDER_PASSWORD=your_app_password

WEATHER_API_KEY=your_openweather_api_key
NEWS_API_KEY=your_newsapi_key

DEFAULT_CITY=London
DEFAULT_NEWS_CATEGORY=technology
```

---

### Required API Keys

* OpenWeatherMap → Weather data
* NewsAPI → News headlines
* Gmail App Password → Email feature

---

## 🚀 Usage

Start the assistant:

```bash
python main.py
```

### Example Commands

* "Open Notepad"
* "What's the time?"
* "Create folder reports"
* "Take a screenshot"
* "Play music"
* "Search for files"
* "Exit"

---

## 🧩 Adding New Commands

### Simple Command Example

```python
if 'shutdown' in command:
    os.system('shutdown /s /t 10')
```

### Parameterized Command

```python
def custom_action(self, param):
    return perform_task(param)
```

---

## 🛠 Troubleshooting

### Microphone Issues

* Check Windows privacy settings
* Ensure mic is connected

### Speech Recognition Issues

```bash
pip install --upgrade SpeechRecognition
```

### TTS Issues

```bash
pip install pyttsx3==2.90
```

### Email Issues

* Use Gmail App Password (not normal password)
* Enable 2FA

---

## ⚠️ Known Limitations

* Requires internet for speech recognition
* English-only commands
* Cannot process multiple commands at once
* High CPU usage during listening
* Limited file search depth

---

## 📁 Project Structure

```
voice-assistant/
├── main.py
├── config.py
├── requirements.txt
├── .env
├── modules/
│   ├── voice_recognizer.py
│   ├── command_processor.py
│   ├── command_mapper.py
│   ├── action_executor.py
│   └── tts_engine.py
```

---

## 📄 License

This project is developed for **educational and productivity purposes**.

---

## 🙌 Credits

* Google Speech Recognition API
* pyttsx3 (Text-to-Speech)
* OpenWeatherMap API
* NewsAPI
