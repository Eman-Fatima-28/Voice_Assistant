from __future__ import annotations

import os
import sys
import re
import shutil
import subprocess
import webbrowser
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Optional, Any, Callable, List

# Brightness control (Windows only)
try:
    import screen_brightness_control as sbc
    BRIGHTNESS_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Brightness control not available: {e}")
    BRIGHTNESS_AVAILABLE = False
    sbc = None


# Optional dependencies
try:
    import pywhatkit
except ImportError:
    pywhatkit = None

try:
    import psutil
except ImportError:
    psutil = None

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

try:
    import pyautogui
except ImportError:
    pyautogui = None


try:
    import requests
except ImportError:
    requests = None

try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
except ImportError:
    smtplib = None

try:
    import imaplib
    import email
except ImportError:
    imaplib = None

from config import Config


@dataclass
class ExecResult:
    ok: bool
    message: str
    action: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: float = 0.0


def _now_ts() -> float:
    return datetime.now().timestamp()


class ActionExecutor:
    """Complete system automation executor"""

    def __init__(self, logger: Optional[Callable[[str], None]] = None):
        self.logger = logger or (lambda msg: print(msg))

        self.downloads_dir = Config.DOWNLOADS_DIR
        self.project_base_dir = Config.PROJECTS_DIR
        self.music_dir = Config.MUSIC_DIR
        self.screenshots_dir = Config.SCREENSHOTS_DIR

        self.safe_base_dirs: List[Path] = [
            self.downloads_dir.resolve(),
            self.project_base_dir.resolve(),
            self.screenshots_dir.resolve(),
        ]

        self.app_map = self._default_app_map()
        self.website_map = self._default_website_map()

        # Initialize brightness control
        self._current_brightness = 50
        self._init_brightness()



    def _init_brightness(self):
        """Initialize brightness control"""
        if not BRIGHTNESS_AVAILABLE:
            print("⚠️  Brightness control library not installed")
            print("   Install: pip install screen-brightness-control")
            self._current_brightness = 50
            return
        
        try:
            # Get current brightness
            brightness = sbc.get_brightness()
            if isinstance(brightness, list):
                self._current_brightness = int(brightness[0])
            else:
                self._current_brightness = int(brightness)
            
            print(f"✅ Brightness control initialized. Current brightness: {self._current_brightness}%")
        
        except Exception as e:
            print(f"⚠️  Brightness control initialization failed: {e}")
            self._current_brightness = 50

    def _default_app_map(self): return {}
    def _default_website_map(self): return {}

    # ==================== MAIN DISPATCHER ====================

    def execute(self, action: str, **kwargs) -> ExecResult:
        """Main execution dispatcher"""
        action = (action or "").strip().lower()
        ts = _now_ts()

        action_map = {
            # Apps
            'open_app': lambda: self.open_app(kwargs.get('app'), timestamp=ts),
            'close_app': lambda: self.close_app(kwargs.get('app'), timestamp=ts),

            # Web
            'open_website': lambda: self.open_website(kwargs.get('site'), timestamp=ts),
            'web_search': lambda: self.web_search(kwargs.get('query'), timestamp=ts),

            # Folders
            'create_project_folder': lambda: self.create_project_folder(
                base_dir=kwargs.get('base_dir'),
                project_name=kwargs.get('project_name', 'Project'),
                use_today=kwargs.get('use_today', True),
                timestamp=ts
            ),
            'create_folder': lambda: self.create_folder(
                base_dir=kwargs.get('base_dir'),
                folder_name=kwargs.get('folder_name'),
                timestamp=ts
            ),

            # File Management
            'cleanup_downloads': lambda: self.cleanup_downloads(
                downloads_dir=kwargs.get('downloads_dir'),
                delete_temp=kwargs.get('delete_temp', False),
                confirm_delete=kwargs.get('confirm_delete', False),
                timestamp=ts
            ),
            'rename_file': lambda: self.rename_file(
                old_path=kwargs.get('old_path'),
                new_name=kwargs.get('new_name'),
                timestamp=ts
            ),
            'search_files': lambda: self.search_files(
                query=kwargs.get('query'),
                search_dir=kwargs.get('search_dir'),
                timestamp=ts
            ),
            'take_screenshot': lambda: self.take_screenshot(
                save_dir=kwargs.get('save_dir'),
                timestamp=ts
            ),

            # Media
            'play_music': lambda: self.play_music(
                music_dir=kwargs.get('music_dir'),
                timestamp=ts
            ),
            'play_youtube': lambda: self.play_youtube(
                query=kwargs.get('query'),
                timestamp=ts
            ),

            # System Info
            'get_time': lambda: self.get_time(timestamp=ts),
            'get_date': lambda: self.get_date(timestamp=ts),
            'get_weather': lambda: self.get_weather(
                city=kwargs.get('city', Config.DEFAULT_CITY),
                timestamp=ts
            ),
            'get_news': lambda: self.get_news(
                category=kwargs.get('category', Config.DEFAULT_NEWS_CATEGORY),
                timestamp=ts
            ),
            
            # System Controls - BRIGHTNESS
            'set_brightness': lambda: self.set_brightness(level=kwargs.get('level', 50), timestamp=ts),
            'brightness_up': lambda: self.brightness_up(timestamp=ts),
            'brightness_down': lambda: self.brightness_down(timestamp=ts),

             # System Controls - WIFI
            'toggle_wifi': lambda: self.toggle_wifi(enable=kwargs.get('enable', True), timestamp=ts),

            # Window/UI Control
            'switch_window': lambda: self.switch_window(timestamp=ts),
            'scroll_down': lambda: self.scroll_page('down', timestamp=ts),
            'scroll_up': lambda: self.scroll_page('up', timestamp=ts),
            'type_text': lambda: self.type_text(
                text=kwargs.get('text'),
                timestamp=ts
            ),

            # Email
            'send_email': lambda: self.send_email(
                to=kwargs.get('to'),
                subject=kwargs.get('subject'),
                body=kwargs.get('body'),
                timestamp=ts
            ),
            'read_emails': lambda: self.read_latest_emails(
                count=kwargs.get('count', 5),
                timestamp=ts
            ),
        }

        try:
            if action in action_map:
                return action_map[action]()
            else:
                return ExecResult(
                    ok=False,
                    message=f"Unknown action: {action}",
                    action=action,
                    error="UnknownAction",
                    timestamp=ts
                )
        except Exception as e:
            return ExecResult(
                ok=False,
                message="Task execution failed.",
                action=action,
                error=str(e),
                timestamp=ts
            )

    # ==================== APPLICATIONS ====================

    def open_app(self, app: Optional[str], *, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        if not app:
            return ExecResult(False, "No application specified.", "open_app",
                              error="MissingApp", timestamp=ts)

        key = app.strip().lower()
        target = self.app_map.get(key, app.strip())
        target = os.path.expandvars(target)

        try:
            if os.name == "nt":
                if target.endswith('.exe') and os.path.exists(target):
                    os.startfile(target)
                else:
                    subprocess.Popen(target, shell=True)
                return ExecResult(True, f"Opening {app}.", "open_app",
                                  data={"app": app}, timestamp=ts)
            else:
                subprocess.Popen(["open", target] if sys.platform == "darwin" else [target])
                return ExecResult(True, f"Opening {app}.", "open_app",
                                  data={"app": app}, timestamp=ts)
        except Exception as e:
            return ExecResult(False, f"Unable to open {app}. Make sure it's installed.", "open_app",
                              data={"app": app, "error": str(e)}, error=str(e), timestamp=ts)

    def close_app(self, app: Optional[str], *, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        if psutil is None:
            return ExecResult(False, "psutil not installed.", "close_app", error="LibraryMissing", timestamp=ts)
        if not app:
            return ExecResult(False, "No application specified.", "close_app", error="MissingApp", timestamp=ts)

        try:
            app_lower = app.lower()
            closed = False
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    if app_lower in proc.info['name'].lower():
                        proc.terminate()
                        closed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if closed:
                return ExecResult(True, f"Closed {app}.", "close_app", timestamp=ts)
            else:
                return ExecResult(False, f"{app} is not running.", "close_app", error="NotRunning", timestamp=ts)
        except Exception as e:
            return ExecResult(False, f"Unable to close {app}.", "close_app", error=str(e), timestamp=ts)


    # ==================== WEBSITES ====================
    
    def open_website(self, site: Optional[str], *, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        if not site:
            return ExecResult(False, "No website specified.", "open_website", error="MissingSite", timestamp=ts)
        
        key = site.strip().lower()
        url = self.website_map.get(key)
        
        if not url:
            candidate = site.strip()
            if re.match(r"^https?://", candidate):
                url = candidate
            else:
                url = "https://" + candidate
        
        try:
            webbrowser.open(url)
            return ExecResult(True, f"Opening {site}.", "open_website", data={"url": url}, timestamp=ts)
        except Exception as e:
            return ExecResult(False, "Unable to open website.", "open_website", error=str(e), timestamp=ts)
    
    def web_search(self, query: Optional[str], *, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        if not query:
            return ExecResult(False, "No search query provided.", "web_search", error="MissingQuery", timestamp=ts)
        
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            return ExecResult(True, f"Searching for {query}.", "web_search", data={"query": query}, timestamp=ts)
        except Exception as e:
            return ExecResult(False, "Search failed.", "web_search", error=str(e), timestamp=ts)
    
    # ==================== FOLDERS ====================
    
    def create_project_folder(self, *, base_dir: Optional[str | Path], project_name: str = "Project",
                             use_today: bool = True, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        base = Path(base_dir) if base_dir else self.project_base_dir
        base = base.expanduser()
        
        if not self._is_safe_path(base):
            return ExecResult(False, "Access denied.", "create_project_folder", error="UnsafePath", timestamp=ts)
        
        day = date.today().isoformat() if use_today else ""
        safe_name = self._sanitize_name(project_name)
        folder_name = f"{safe_name}_{day}" if day else safe_name
        
        try:
            created_path = self._mkdir_unique(base, folder_name)
            return ExecResult(True, f"Folder created: {created_path.name}", "create_project_folder",
                            data={"path": str(created_path)}, timestamp=ts)
        except Exception as e:
            return ExecResult(False, "Unable to create folder.", "create_project_folder", error=str(e), timestamp=ts)
    
    def create_folder(self, *, base_dir: Optional[str | Path], folder_name: Optional[str],
                     timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        if not folder_name:
            return ExecResult(False, "No folder name provided.", "create_folder", error="MissingName", timestamp=ts)
        
        base = Path(base_dir) if base_dir else self.project_base_dir
        base = base.expanduser()
        
        if not self._is_safe_path(base):
            return ExecResult(False, "Access denied.", "create_folder", error="UnsafePath", timestamp=ts)
        
        name = self._sanitize_name(folder_name)
        try:
            created_path = self._mkdir_unique(base, name)
            return ExecResult(True, f"Folder created: {created_path.name}", "create_folder",
                            data={"path": str(created_path)}, timestamp=ts)
        except Exception as e:
            return ExecResult(False, "Unable to create folder.", "create_folder", error=str(e), timestamp=ts)
    
    # ==================== FILE MANAGEMENT ====================
    
    def cleanup_downloads(self, *, downloads_dir: Optional[str | Path], delete_temp: bool = False,
                         confirm_delete: bool = False, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        dl = Path(downloads_dir) if downloads_dir else self.downloads_dir
        dl = dl.expanduser()
        
        if not self._is_safe_path(dl):
            return ExecResult(False, "Access denied.", "cleanup_downloads", error="UnsafePath", timestamp=ts)
        
        if not dl.exists():
            return ExecResult(False, "Downloads folder not found.", "cleanup_downloads", error="NotFound", timestamp=ts)
        
        categories = {
            "Documents": {".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"},
            "Images": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"},
            "Videos": {".mp4", ".mkv", ".avi", ".mov"},
            "Audio": {".mp3", ".wav", ".m4a", ".aac"},
            "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
            "Installers": {".exe", ".msi", ".apk"},
            "Code": {".py", ".js", ".ts", ".java", ".cpp", ".c", ".html", ".css", ".json"},
        }
        temp_exts = {".tmp", ".crdownload", ".part"}
        
        moved = []
        deleted = []
        skipped = []
        
        try:
            for item in dl.iterdir():
                if item.is_dir():
                    continue
                
                ext = item.suffix.lower()
                
                if ext in temp_exts and delete_temp and confirm_delete:
                    try:
                        item.unlink()
                        deleted.append(item.name)
                    except:
                        skipped.append(item.name)
                    continue
                
                dest_folder_name = self._category_for_ext(ext, categories)
                dest_folder = dl / dest_folder_name
                dest_folder.mkdir(exist_ok=True)
                
                dest_path = dest_folder / item.name
                dest_path = self._unique_path(dest_path)
                
                try:
                    shutil.move(str(item), str(dest_path))
                    moved.append({"from": item.name, "to": f"{dest_folder_name}/{dest_path.name}"})
                except:
                    skipped.append(item.name)
            
            return ExecResult(True, "Downloads organized.", "cleanup_downloads",
                            data={"moved": moved, "deleted": deleted}, timestamp=ts)
        
        except Exception as e:
            return ExecResult(False, "Cleanup failed.", "cleanup_downloads", error=str(e), timestamp=ts)
    
    def rename_file(self, *, old_path: str, new_name: str, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        
        try:
            old = Path(old_path).expanduser()
            
            if not self._is_safe_path(old.parent):
                return ExecResult(False, "Access denied.", "rename_file", error="UnsafePath", timestamp=ts)
            
            if not old.exists():
                return ExecResult(False, "File not found.", "rename_file", error="NotFound", timestamp=ts)
            
            safe_name = self._sanitize_name(new_name)
            new_path = old.parent / (safe_name + old.suffix)
            
            old.rename(new_path)
            return ExecResult(True, f"Renamed to {new_path.name}.", "rename_file",
                            data={"new_path": str(new_path)}, timestamp=ts)
        
        except Exception as e:
            return ExecResult(False, "Rename failed.", "rename_file", error=str(e), timestamp=ts)
    
    def search_files(self, *, query: str, search_dir: Optional[Path] = None,
                    timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        
        if not query:
            return ExecResult(False, "No search query.", "search_files", error="MissingQuery", timestamp=ts)
        
        search_dir = search_dir or Path.home()
        results = []
        
        try:
            query_lower = query.lower()
            
            for root, dirs, files in os.walk(search_dir):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if query_lower in file.lower():
                        results.append(os.path.join(root, file))
                    
                    if len(results) >= 20:
                        break
                
                if len(results) >= 20:
                    break
            
            if results:
                return ExecResult(True, f"Found {len(results)} file(s).", "search_files",
                                data={"results": results}, timestamp=ts)
            else:
                return ExecResult(False, "No files found.", "search_files", error="NoResults", timestamp=ts)
        
        except Exception as e:
            return ExecResult(False, "Search failed.", "search_files", error=str(e), timestamp=ts)
    
    def take_screenshot(self, *, save_dir: Optional[Path] = None, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        
        if ImageGrab is None:
            return ExecResult(False, "Screenshot library missing.", "screenshot", error="LibraryMissing", timestamp=ts)
        
        try:
            save_dir = save_dir or self.screenshots_dir
            save_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = save_dir / filename
            
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            return ExecResult(True, "Screenshot saved.", "screenshot", data={"path": str(filepath)}, timestamp=ts)
        
        except Exception as e:
            return ExecResult(False, "Screenshot failed.", "screenshot", error=str(e), timestamp=ts)
    
    # ==================== MEDIA ====================
    
    def play_music(self, *, music_dir: Optional[str | Path], timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        mdir = Path(music_dir).expanduser() if music_dir else self.music_dir
        
        if not mdir.exists():
            return ExecResult(False, "Music folder not found.", "play_music", error="NotFound", timestamp=ts)
        
        exts = [".mp3", ".wav", ".m4a", ".aac"]
        files = [p for p in mdir.iterdir() if p.is_file() and p.suffix.lower() in exts]
        
        if not files:
            return ExecResult(False, "No music files found.", "play_music", error="NoFiles", timestamp=ts)
        
        try:
            self._open_file_with_default_app(files[0])
            return ExecResult(True, "Playing music.", "play_music", data={"file": str(files[0])}, timestamp=ts)
        except Exception as e:
            return ExecResult(False, "Playback failed.", "play_music", error=str(e), timestamp=ts)
    
    def play_youtube(self, *, query: Optional[str], timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        if not query:
            return ExecResult(False, "No video query.", "play_youtube", error="MissingQuery", timestamp=ts)
        
        if pywhatkit:
            try:
                pywhatkit.playonyt(query)
                return ExecResult(True, f"Playing {query}.", "play_youtube", data={"query": query}, timestamp=ts)
            except:
                pass
        
        try:
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(url)
            return ExecResult(True, f"Opening YouTube for {query}.", "play_youtube", data={"query": query}, timestamp=ts)
        except Exception as e:
            return ExecResult(False, "YouTube playback failed.", "play_youtube", error=str(e), timestamp=ts)
    
    # ==================== SYSTEM INFO ====================
    
    def get_time(self, *, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        now = datetime.now().strftime("%I:%M %p").lstrip("0")
        return ExecResult(True, f"The time is {now}.", "get_time", data={"time": now}, timestamp=ts)
    
    def get_date(self, *, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        today = datetime.now().strftime("%A, %B %d, %Y")
        return ExecResult(True, f"Today is {today}.", "get_date", data={"date": today}, timestamp=ts)
    
    def get_weather(self, *, city: str, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        
        if not Config.WEATHER_API_KEY or requests is None:
            return ExecResult(False, "Weather service unavailable.", "get_weather", error="NotConfigured", timestamp=ts)
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={Config.WEATHER_API_KEY}&units=metric"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            
            if resp.status_code == 200:
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                msg = f"In {city}, it's {temp}°C with {desc}."
                return ExecResult(True, msg, "get_weather", data=data, timestamp=ts)
            else:
                return ExecResult(False, "Weather unavailable.", "get_weather", error="APIError", timestamp=ts)
        
        except Exception as e:
            return ExecResult(False, "Weather fetch failed.", "get_weather", error=str(e), timestamp=ts)
    
    def get_news(self, *, category: str, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        
        if not Config.NEWS_API_KEY or requests is None:
            return ExecResult(False, "News service unavailable.", "get_news", error="NotConfigured", timestamp=ts)
        
        try:
            url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={Config.NEWS_API_KEY}"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            
            if data.get('status') == 'ok':
                articles = data['articles'][:3]
                headlines = [a['title'] for a in articles]
                msg = f"Top {category} news: " + ". ".join(headlines)
                return ExecResult(True, msg, "get_news", data={"headlines": headlines}, timestamp=ts)
            else:
                return ExecResult(False, "News unavailable.", "get_news", error="APIError", timestamp=ts)
        
        except Exception as e:
            return ExecResult(False, "News fetch failed.", "get_news", error=str(e), timestamp=ts)




    # ==================== BRIGHTNESS CONTROL ====================

    def set_brightness(self, *, level: int, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        if not BRIGHTNESS_AVAILABLE:
            return ExecResult(False, "Brightness control not available.", "set_brightness", error="NO_BRIGHTNESS_LIBRARY", timestamp=ts)
        try:
            level = max(0, min(100, int(level)))
            sbc.set_brightness(level)
            self._current_brightness = level
            print(f"💡 Brightness set to {level}%")
            return ExecResult(True, f"Brightness set to {level} percent.", "set_brightness", data={"level": level}, timestamp=ts)
        except Exception as e:
            return ExecResult(False, "Failed to change brightness.", "set_brightness", error=str(e), timestamp=ts)

    def brightness_up(self, *, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        if not BRIGHTNESS_AVAILABLE:
            return ExecResult(False, "Brightness control not available.", "brightness_up", error="NO_BRIGHTNESS_LIBRARY", timestamp=ts)
        try:
            brightness = sbc.get_brightness()
            current = int(brightness[0]) if isinstance(brightness, list) else int(brightness)
            return self.set_brightness(level=min(100, current + 10), timestamp=ts)
        except Exception as e:
            return ExecResult(False, "Failed to increase brightness.", "brightness_up", error=str(e), timestamp=ts)

    def brightness_down(self, *, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        if not BRIGHTNESS_AVAILABLE:
            return ExecResult(False, "Brightness control not available.", "brightness_down", error="NO_BRIGHTNESS_LIBRARY", timestamp=ts)
        try:
            brightness = sbc.get_brightness()
            current = int(brightness[0]) if isinstance(brightness, list) else int(brightness)
            return self.set_brightness(level=max(0, current - 10), timestamp=ts)
        except Exception as e:
            return ExecResult(False, "Failed to decrease brightness.", "brightness_down", error=str(e), timestamp=ts)
    
    def toggle_wifi(self, *, enable: bool, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        
        try:
            if os.name == 'nt':
                action = "connect" if enable else "disconnect"
                subprocess.run(f'netsh interface set interface "Wi-Fi" {action}', shell=True, check=True)
                status = "enabled" if enable else "disabled"
                return ExecResult(True, f"Wi-Fi {status}.", "toggle_wifi", timestamp=ts)
            else:
                return ExecResult(False, "Wi-Fi control only on Windows.", "toggle_wifi", error="Unsupported", timestamp=ts)
        
        except Exception as e:
            return ExecResult(False, "Wi-Fi toggle failed.", "toggle_wifi", error=str(e), timestamp=ts)
    
    # ==================== WINDOW/UI CONTROL ====================
    
    def switch_window(self, *, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        
        if pyautogui is None:
            return ExecResult(False, "pyautogui missing.", "switch_window", error="LibraryMissing", timestamp=ts)
        
        try:
            pyautogui.keyDown('alt')
            pyautogui.press('tab')
            pyautogui.keyUp('alt')
            return ExecResult(True, "Switched window.", "switch_window", timestamp=ts)
        
        except Exception as e:
            return ExecResult(False, "Window switch failed.", "switch_window", error=str(e), timestamp=ts)
    
    def scroll_page(self, direction: str, *, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        
        if pyautogui is None:
            return ExecResult(False, "pyautogui missing.", "scroll_page", error="LibraryMissing", timestamp=ts)
        
        try:
            amount = -3 if direction == 'down' else 3
            pyautogui.scroll(amount * 100)
            return ExecResult(True, f"Scrolled {direction}.", "scroll_page", timestamp=ts)
        
        except Exception as e:
            return ExecResult(False, "Scroll failed.", "scroll_page", error=str(e), timestamp=ts)
    
    def type_text(self, *, text: str, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        
        if pyautogui is None:
            return ExecResult(False, "pyautogui missing.", "type_text", error="LibraryMissing", timestamp=ts)
        
        if not text:
            return ExecResult(False, "No text provided.", "type_text", error="MissingText", timestamp=ts)
        
        try:
            pyautogui.write(text, interval=0.05)
            return ExecResult(True, "Text typed.", "type_text", data={"text": text}, timestamp=ts)
        
        except Exception as e:
            return ExecResult(False, "Typing failed.", "type_text", error=str(e), timestamp=ts)
    
    # ==================== EMAIL ====================
    
    def send_email(self, *, to: str, subject: str, body: str, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
    
        if not Config.SENDER_EMAIL or not Config.SENDER_PASSWORD or smtplib is None:
            return ExecResult(False, "Email not configured in .env file.", "send_email", error="NotConfigured", timestamp=ts)
    
        if not to or not subject or not body:
            return ExecResult(False, "Missing email details.", "send_email", error="MissingDetails", timestamp=ts)
    
        try:
            print(f"\n📧 Sending email to {to}...")
        
            msg = MIMEMultipart()
            msg['From'] = Config.SENDER_EMAIL
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
        
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
            server.starttls()
            server.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
        
            print(f"✅ Email sent successfully!")
        
            return ExecResult(True, f"Email sent to {to}.", "send_email", timestamp=ts)
    
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Authentication failed: {e}")
            return ExecResult(False, "Email authentication failed. Check your App Password.", "send_email", error=str(e), timestamp=ts)
    
        except Exception as e:
            print(f"❌ Email error: {e}")
            return ExecResult(False, "Email send failed.", "send_email", error=str(e), timestamp=ts)
    
    def read_latest_emails(self, *, count: int = 5, timestamp: Optional[float] = None) -> ExecResult:
        ts = timestamp or _now_ts()
        
        if not Config.SENDER_EMAIL or not Config.SENDER_PASSWORD or imaplib is None:
            return ExecResult(False, "Email not configured.", "read_emails", error="NotConfigured", timestamp=ts)
        
        try:
            print(f"\n📬 Reading emails...")
            
            mail = imaplib.IMAP4_SSL('imap.gmail.com', timeout=10)
            mail.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
            mail.select('inbox')
            
            _, search_data = mail.search(None, 'ALL')
            mail_ids = search_data[0].split()
            
            if not mail_ids:
                mail.logout()
                return ExecResult(True, "No emails found.", "read_emails", data={"emails": []}, timestamp=ts)
            
            emails = []
            for mail_id in mail_ids[-count:]:
                try:
                    _, data = mail.fetch(mail_id, '(RFC822)')
                    msg = email.message_from_bytes(data[0][1])
                    
                    emails.append({
                        'from': msg.get('From', 'Unknown'),
                        'subject': msg.get('Subject', 'No Subject'),
                        'date': msg.get('Date', 'Unknown')
                    })
                except:
                    continue
            
            mail.logout()
            
            if emails:
                subjects = [e['subject'] for e in emails[:3]]
                msg_text = f"You have {len(emails)} recent emails. " + ". ".join(subjects)
            else:
                msg_text = "Unable to read emails."
            
            print(f"✅ Read {len(emails)} emails")
            
            return ExecResult(True, msg_text, "read_emails", data={"emails": emails}, timestamp=ts)
        
        except Exception as e:
            print(f"❌ Email read error: {e}")
            return ExecResult(False, "Email read failed.", "read_emails", error=str(e), timestamp=ts)
    
    # ==================== HELPERS ====================
    
    def _default_app_map(self) -> Dict[str, str]:
        if os.name == "nt":
            return {
                "notepad": "notepad",
                "calculator": "calc",
                "chrome": "chrome",
                "browser": "chrome",
                "vscode": "code",
                "vs code": "code",
                "excel": "excel",
                "word": "winword",
                "spotify": "spotify",
            }
        return {
            "vscode": "code",
            "browser": "firefox",
        }
    
    def _default_website_map(self) -> Dict[str, str]:
        return {
            "gmail": "https://mail.google.com/",
            "youtube": "https://www.youtube.com/",
            "google": "https://www.google.com/",
            "github": "https://github.com/",
        }
    
    def _sanitize_name(self, name: str) -> str:
        name = name.strip()
        name = re.sub(r"[^\w\- ]+", "", name)
        name = re.sub(r"\s+", "_", name)
        return name[:80] if len(name) > 80 else name
    
    def _mkdir_unique(self, base: Path, folder_name: str) -> Path:
        base.mkdir(parents=True, exist_ok=True)
        target = base / folder_name
        target = self._unique_path(target)
        target.mkdir(parents=True, exist_ok=False)
        return target
    
    def _unique_path(self, path: Path) -> Path:
        if not path.exists():
            return path
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        for i in range(1, 5000):
            candidate = parent / f"{stem}_{i}{suffix}"
            if not candidate.exists():
                return candidate
        raise RuntimeError("Unable to create unique name.")
    
    def _category_for_ext(self, ext: str, categories: Dict[str, set]) -> str:
        for cat, exts in categories.items():
            if ext in exts:
                return cat
        return "Others"
    
    def _is_safe_path(self, base: Path) -> bool:
        try:
            base_res = base.resolve()
        except:
            return False
        
        for safe in self.safe_base_dirs:
            try:
                safe_res = safe.resolve()
                if safe_res == base_res or str(base_res).startswith(str(safe_res) + os.sep):
                    return True
            except:
                continue
        return False
    
    def _open_file_with_default_app(self, path: Path) -> None:
        if os.name == "nt":
            os.startfile(str(path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])

   