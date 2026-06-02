import re
from typing import Optional, Tuple, List


class CommandMapper:
    """
    Maps natural language input to standardized commands.
    Handles variations like:
      - "open notepad" / "notepad open" / "launch notepad" / "start notepad"
      - "what's the time" / "check time" / "tell me the time"
    """

    def __init__(self):
        # Action keywords
        self.open_keywords = ['open', 'launch', 'start', 'run', 'execute']
        self.close_keywords = ['close', 'shut', 'exit', 'quit', 'kill', 'stop']
        self.create_keywords = ['create', 'make', 'new']
        self.search_keywords = ['search', 'find', 'look for', 'locate']
        self.play_keywords = ['play', 'start playing', 'put on']
        self.volume_keywords = ['volume', 'sound']
        self.brightness_keywords = ['brightness', 'screen brightness']

        # Question keywords
        self.time_keywords = ['time', 'clock']
        self.date_keywords = ['date', 'day', 'today']
        self.weather_keywords = ['weather', 'temperature', 'forecast']
        self.news_keywords = ['news', 'headlines', 'updates']

        # App name variations
        self.app_aliases = {
            'notepad': ['notepad', 'text editor', 'note pad'],
            'calculator': ['calculator', 'calc', 'calculate'],
            'excel': ['excel', 'spreadsheet'],
            'word': ['word', 'document', 'doc'],
            'chrome': ['chrome', 'browser', 'google chrome'],
            'firefox': ['firefox', 'mozilla'],
            'vscode': ['vscode', 'vs code', 'visual studio code', 'code editor'],
            'spotify': ['spotify', 'music player'],
            'zoom': ['zoom', 'zoom meeting'],
        }

        # Website aliases
        self.site_aliases = {
            'gmail': ['gmail', 'email', 'mail'],
            'youtube': ['youtube', 'video'],
            'google': ['google', 'search engine'],
            'github': ['github', 'git hub'],
        }

    # -------------------- Main Normalization -------------------- #

    def normalize(self, command: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Normalize command to (action, target, parameter)
        """
        command = command.lower().strip()

        # Remove filler words
        command = self._remove_fillers(command)

        # 1. EXIT/QUIT COMMANDS
        if any(word in command for word in ['exit', 'quit', 'goodbye', 'bye', 'stop assistant', 'stop listening']):
            return ('exit', None, None)

        # 2. TIME QUERIES
        time_triggers = ['time', 'clock', "what's the time", 'whats the time', 'tell me time',
                         'check time', 'current time', 'what time is it', 'what time it is']
        if any(trigger in command for trigger in time_triggers):
            return ('get_time', None, None)

        # 3. DATE QUERIES
        if any(word in command for word in ['date', 'day', 'today', "what's", 'whats']) and 'time' not in command:
            if any(phrase in command for phrase in ['date', 'day is it', 'day is today', 'today', 'todays date']):
                return ('get_date', None, None)

        # 4. WEATHER QUERIES
        if any(word in command for word in ['weather', 'temperature', 'forecast', 'hot', 'cold', 'raining']):
            city = None
            if ' in ' in command:
                city = command.split(' in ')[-1].strip()
            elif ' at ' in command:
                city = command.split(' at ')[-1].strip()
            elif ' for ' in command:
                city = command.split(' for ')[-1].strip()

            if city:
                for word in ['weather', 'temperature', 'forecast', 'the']:
                    city = city.replace(word, '').strip()
            return ('get_weather', None, city)

        # 5. NEWS QUERIES
        news_triggers = ['news', 'headlines', 'updates', 'latest news']
        if any(trigger in command for trigger in news_triggers):
            category = None
            categories = ['technology', 'business', 'sports', 'entertainment', 'science', 'health']
            for cat in categories:
                if cat in command:
                    category = cat
                    break
            return ('get_news', None, category)

        # 6. OPEN APPLICATION
        open_triggers = ['open', 'launch', 'start', 'run', 'execute']
        if any(trigger in command for trigger in open_triggers):
            app_name = command
            for trigger in open_triggers:
                app_name = app_name.replace(trigger, '')
            app_name = app_name.strip()

            site_keywords = ['gmail', 'youtube', 'google', 'github', 'facebook', 'twitter', 'mail', 'email', '.com', 'www']
            if any(keyword in app_name for keyword in site_keywords):
                return ('open_website', app_name, None)
            if app_name:
                return ('open_app', app_name, None)

        # 7. CLOSE APPLICATION
        close_triggers = ['close', 'shut', 'exit', 'quit', 'kill', 'stop', 'end']
        if any(keyword in command for keyword in ['close', 'shut down', 'shut']) and 'assistant' not in command:
            app_name = command
            for trigger in close_triggers:
                app_name = app_name.replace(trigger, '')
            app_name = app_name.strip()
            if app_name:
                return ('close_app', app_name, None)

        # 8. CREATE FOLDER
        if 'folder' in command or 'directory' in command:
            if 'create' in command or 'make' in command or 'new' in command:
                folder_name = command
                for word in ['create', 'make', 'new', 'folder', 'directory', 'named', 'called', 'project']:
                    folder_name = folder_name.replace(word, '')
                folder_name = folder_name.strip() or 'NewFolder'
                action_type = 'create_project_folder' if 'project' in command else 'create_folder'
                return (action_type, None, folder_name)

        # 9. CLEAN DOWNLOADS
        clean_triggers = ['clean download', 'clean downloads', 'organize download', 'organize downloads', 'cleanup download', 'tidy download']
        if any(trigger in command for trigger in clean_triggers):
            return ('cleanup_downloads', None, None)

        # 10. SEARCH FILES
        if any(word in command for word in ['search', 'find', 'look', 'locate']):
            if 'file' in command or 'document' in command or 'folder' in command:
                query = command
                for word in ['search', 'for', 'find', 'look', 'locate', 'file', 'files', 'document', 'documents', 'folder', 'folders', 'named', 'called']:
                    query = query.replace(word, '')
                query = query.strip()
                if query:
                    return ('search_files', None, query)
                return ('search_files', None, 'document')

        # 11. SCREENSHOT
        screenshot_triggers = ['screenshot', 'screen shot', 'capture screen', 'take screenshot', 'snap screen', 'screen capture', 'take picture of screen']
        if any(trigger in command for trigger in screenshot_triggers):
            return ('take_screenshot', None, None)

        # 12. PLAY MUSIC
        music_triggers = ['play music', 'play song', 'play songs', 'start music', 'music play']
        if any(trigger in command for trigger in music_triggers) and 'youtube' not in command:
            return ('play_music', None, None)

        # 13. PLAY YOUTUBE
        youtube_triggers = ['play on youtube', 'youtube play', 'play youtube', 'on youtube', 'search youtube', 'youtube search']
        if any(trigger in command for trigger in youtube_triggers) or ('play' in command and 'youtube' in command):
            query = command
            for trigger in ['play', 'youtube', 'on', 'video', 'search']:
                query = query.replace(trigger, '')
            return ('play_youtube', None, query.strip() or 'music')

        # 14. VOLUME CONTROL
        if 'volume' in command or 'sound' in command:
            if any(word in command for word in ['up', 'increase', 'raise', 'higher', 'louder']):
                return ('volume_up', None, None)
            elif any(word in command for word in ['down', 'decrease', 'lower', 'reduce', 'quieter']):
                return ('volume_down', None, None)
            elif 'mute' in command or 'silent' in command or 'off' in command:
                return ('volume_mute', None, None)
            else:
                numbers = re.findall(r'\d+', command)
                level = numbers[0] if numbers else '50'
                return ('set_volume', None, level)
        # Brightness
        if 'brightness' in command or 'screen brightness' in command:
            if any(word in command for word in ['up', 'increase', 'raise', 'higher', 'brighter']):
                return ('brightness_up', None, None)
            elif any(word in command for word in ['down', 'decrease', 'lower', 'reduce', 'dimmer', 'dim']):
                return ('brightness_down', None, None)
            else:
        # Extract specific brightness level
                import re
                numbers = re.findall(r'\d+', command)
                level = numbers[0] if numbers else '50'
                return ('set_brightness', None, level)

        # 15. WEB SEARCH
        search_web_triggers = ['search for', 'google', 'search', 'look up', 'find out about']
        if any(trigger in command for trigger in search_web_triggers) and 'file' not in command:
            query = command
            for trigger in search_web_triggers:
                query = query.replace(trigger, '')
            query = query.strip()
            return ('web_search', None, query)

        # 16. EMAIL
        if any(word in command for word in ['email', 'send mail', 'send message', 'compose email']):
            if any(word in command for word in ['read', 'check', 'show', 'get']):
                return ('read_emails', None, None)
            return ('send_email', None, None)

        # 17. WINDOW CONTROL
        if any(phrase in command for phrase in ['switch window', 'change window', 'next window', 'alt tab', 'switch app', 'change app']):
            return ('switch_window', None, None)

        # 18. SCROLL
        if 'scroll' in command:
            if any(word in command for word in ['down', 'bottom']):
                return ('scroll_down', None, None)
            elif any(word in command for word in ['up', 'top']):
                return ('scroll_up', None, None)

        # 19. TYPE TEXT
        type_triggers = ['type', 'write', 'enter text', 'input']
        if any(trigger in command for trigger in type_triggers):
            text = command
            for trigger in type_triggers:
                text = text.replace(trigger, '')
            text = text.strip()
            if text:
                return ('type_text', None, text)

        # 20. WIFI
        if 'wifi' in command or 'wi-fi' in command or 'internet' in command:
            if any(word in command for word in ['on', 'enable', 'start', 'connect']):
                return ('wifi_on', None, None)
            elif any(word in command for word in ['off', 'disable', 'stop', 'disconnect']):
                return ('wifi_off', None, None)

        # Unable to parse
        return (None, None, None)

    # -------------------- Helper Methods -------------------- #

    def _remove_fillers(self, text: str) -> str:
        """Remove common filler words"""
        fillers = [
            'please', 'can you', 'could you', 'would you',
            'kindly', 'just', 'simply', 'go ahead',
            'i want to', 'i want', 'i need to', 'i need',
            'can you please', 'could you please',
            'for me', 'right now', 'now'
        ]
        for filler in fillers:
            text = text.replace(filler, ' ')

        # Remove 'the', 'a', 'an' only if not part of actual command
        text = ' ' + text + ' '
        text = text.replace(' the ', ' ')
        text = text.replace(' a ', ' ')
        text = text.replace(' an ', ' ')
        return ' '.join(text.split())  # Remove extra spaces

    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number from text"""
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else None


# -------------------- Demo -------------------- #
if __name__ == "__main__":
    mapper = CommandMapper()

    test_commands = [
        "open notepad",
        "notepad open",
        "launch the notepad",
        "what's the time",
        "check time please",
        "tell me the date",
        "play shape of you on youtube",
        "create folder reports",
        "create project folder sales",
        "search for presentation files",
        "take a screenshot",
        "increase volume",
        "set volume to 75",
        "turn on wifi",
        "close chrome",
        "exit",
    ]

    print("Command Mapping Demo:\n")
    for cmd in test_commands:
        action, target, param = mapper.normalize(cmd)
        print(f"'{cmd}'")
        print(f"  → Action: {action}, Target: {target}, Param: {param}\n")
