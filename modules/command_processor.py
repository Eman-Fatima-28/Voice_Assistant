from modules.action_executor import ActionExecutor
from modules.tts_engine import TTSFeedbackEngine
from modules.command_mapper import CommandMapper
from config import Config

# Debugging helper
def log_command(original, action, target, parameter):
    """Debug log for command processing"""
    print(f"\n🔍 DEBUG:")
    print(f"   Original: '{original}'")
    print(f"   → Action: {action}")
    print(f"   → Target: {target}")
    print(f"   → Param: {parameter}\n")

executor = ActionExecutor()
tts = TTSFeedbackEngine()
mapper = CommandMapper()
conf = Config()

# Global state for confirmations
awaiting_delete_confirmation = False
awaiting_email_details = False
email_draft = {}

def handle_email_collection(command: str) -> bool:
    global awaiting_email_details, email_draft

    step = email_draft.get('step')

    # STEP 1: Collect recipient
    if step == 'recipient':
        email_address = command.replace(" at ", "@").replace(" dot ", ".").replace(" ", "")
        
        if "@" not in email_address or "." not in email_address:
            tts.speak_warning("That doesn't sound like a valid email. Please say it again.")
            return True
        
        email_draft['to'] = email_address
        email_draft['step'] = 'subject'
        tts.speak_success(f"Sending to {email_address}. What is the subject?")
        return True

    # STEP 2: Collect subject
    elif step == 'subject':
        if not command.strip():
            tts.speak_warning("I didn't catch the subject. Please say it again.")
            return True
        
        email_draft['subject'] = command.strip()
        email_draft['step'] = 'body'
        tts.speak_success("What should I write in the email?")
        return True

    # STEP 3: Collect body
    elif step == 'body':
        if not command.strip():
            tts.speak_warning("I didn't catch the message. Please say it again.")
            return True
        
        email_draft['body'] = command.strip()
        email_draft['step'] = 'confirm'
        tts.speak_warning("Ready to send. Say yes to send, or no to cancel.")
        return True

    # STEP 4: Confirmation
    elif step == 'confirm':
        if "yes" in command or "send" in command or "confirm" in command:
            tts.speak_success("Sending email now...")
            
            res = executor.execute(
                "send_email",
                to=email_draft.get('to'),
                subject=email_draft.get('subject'),
                body=email_draft.get('body')
            )
            
            awaiting_email_details = False
            email_draft.clear()
            
            if res.ok:
                tts.speak_success(res.message)
            else:
                tts.speak_error(f"Email failed. {res.message}")
            
            return True
        
        elif "no" in command or "cancel" in command:
            awaiting_email_details = False
            email_draft.clear()
            tts.speak_warning("Email cancelled.")
            return True
        
        else:
            tts.speak_warning("Please say yes to send, or no to cancel.")
            return True
    
    else:
        awaiting_email_details = False
        email_draft.clear()
        tts.speak_error("Email process error. Please start over.")
        return True


def process_command(command: str) -> bool:
    """
    Process voice command and execute appropriate action
    Returns True to continue listening, False to exit
    """
    global awaiting_delete_confirmation, awaiting_email_details, email_draft
    
    command = command.lower().strip()
    
    # ==================== CONFIRMATION HANDLING ====================
    
    if awaiting_delete_confirmation:
        if "yes" in command or "confirm" in command or "sure" in command or "ok" in command:
            res = executor.execute(
                "cleanup_downloads",
                delete_temp=True,
                confirm_delete=True
            )
            awaiting_delete_confirmation = False
            tts.speak_success(res.message)
            return True
        
        elif "no" in command or "cancel" in command or "nope" in command:
            awaiting_delete_confirmation = False
            tts.speak_warning("Okay, I will not delete any files.")
            return True
        
        else:
            tts.speak_warning("Please say yes or no.")
            return True
    
    # Email detail collection
    if awaiting_email_details:
        return handle_email_collection(command)
    
    # ==================== COMMAND NORMALIZATION ====================
    
    action, target, parameter = mapper.normalize(command)
    
    # Debug logging (comment out in production)
    log_command(command, action, target, parameter)
    
    if action is None:
        tts.speak_warning("Sorry, I didn't understand that command.")
        return True
    
    # ==================== EXECUTE ACTIONS ====================
    
    try:
        # EXIT
        if action == 'exit':
            tts.speak_success("Goodbye. Have a nice day!")
            return False
        
        # OPEN APP
        elif action == 'open_app':
            app_name = target or parameter
            if app_name:
                res = executor.execute("open_app", app=app_name)
                tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
            else:
                tts.speak_warning("Which application should I open?")
        
        # CLOSE APP
        elif action == 'close_app':
            app_name = target or parameter
            if app_name:
                res = executor.execute("close_app", app=app_name)
                tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
            else:
                tts.speak_warning("Which application should I close?")
        
        # OPEN WEBSITE
        elif action == 'open_website':
            site_name = target or parameter
            if site_name:
                res = executor.execute("open_website", site=site_name)
                tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
            else:
                tts.speak_warning("Which website should I open?")
        
        # WEB SEARCH
        elif action == 'web_search':
            query = parameter or target
            if query:
                res = executor.execute("web_search", query=query)
                tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
            else:
                tts.speak_warning("What do you want me to search for?")
        
        # CREATE PROJECT FOLDER
        elif action == 'create_project_folder':
            folder_name = parameter or target or "Project"
            res = executor.execute(
                "create_project_folder",
                project_name=folder_name,
                use_today=True
            )
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
        
        # CREATE FOLDER
        elif action == 'create_folder':
            folder_name = parameter or target
            if folder_name:
                res = executor.execute("create_folder", folder_name=folder_name)
                tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
            else:
                tts.speak_warning("What should I name the folder?")
        
        # CLEANUP DOWNLOADS
        elif action == 'cleanup_downloads':
            tts.speak_warning("Do you want me to delete temporary files? Say yes or no.")
            awaiting_delete_confirmation = True
        
        # SEARCH FILES
        elif action == 'search_files':
            query = parameter or target
            if query:
                res = executor.execute("search_files", query=query)
                if res.ok and res.data and res.data.get('results'):
                    results = res.data['results'][:5]
                    tts.speak_success(f"Found {len(results)} files. Showing first few.")
                    for i, path in enumerate(results, 1):
                        print(f"{i}. {path}")
                else:
                    tts.speak_error(res.message)
            else:
                tts.speak_warning("What file are you looking for?")
        
        # SCREENSHOT
        elif action == 'take_screenshot':
            res = executor.execute("take_screenshot")
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
        
        # PLAY MUSIC
        elif action == 'play_music':
            res = executor.execute("play_music")
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
        
        # PLAY YOUTUBE
        elif action == 'play_youtube':
            query = parameter or target or "music"
            res = executor.execute("play_youtube", query=query)
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
        
        # GET TIME
        elif action == 'get_time':
            res = executor.execute("get_time")
            tts.speak_success(res.message)
        
        # GET DATE
        elif action == 'get_date':
            res = executor.execute("get_date")
            tts.speak_success(res.message)
        
        # GET WEATHER
        elif action == 'get_weather':
            city = parameter or target or "London"
            res = executor.execute("get_weather", city=city)
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
        
        # GET NEWS
        elif action == 'get_news':
            category = parameter or target or "technology"
            res = executor.execute("get_news", category=category)
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)

# ADD BRIGHTNESS CONTROLS HERE:
        elif action == 'set_brightness':
            level = int(parameter) if parameter and parameter.isdigit() else 50
            res = executor.execute("set_brightness", level=level)
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)

        elif action == 'brightness_up':
            res = executor.execute("brightness_up")
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)

        elif action == 'brightness_down':
            res = executor.execute("brightness_down")
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
        # WIFI CONTROL
        elif action == 'wifi_on':
            res = executor.execute("toggle_wifi", enable=True)
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
        
        elif action == 'wifi_off':
            res = executor.execute("toggle_wifi", enable=False)
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
        
        # WINDOW/UI CONTROLS
        elif action == 'switch_window':
            res = executor.execute("switch_window")
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
        
        elif action == 'scroll_down':
            res = executor.execute("scroll_down")
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
        
        elif action == 'scroll_up':
            res = executor.execute("scroll_up")
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
        
        elif action == 'type_text':
            text = parameter or target
            if text:
                res = executor.execute("type_text", text=text)
                tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
            else:
                tts.speak_warning("What should I type?")
        
        # EMAIL
        elif action == 'send_email':
            if not conf.SENDER_EMAIL or not conf.SENDER_PASSWORD:
                tts.speak_error("Email is not configured. Please set up Gmail credentials in the .env file.")
                return True
            
            tts.speak_success("Starting email. Who should I send this to?")
            awaiting_email_details = True
            email_draft.clear()
            email_draft['step'] = 'recipient'

        elif action == 'read_emails':
            if not conf.SENDER_EMAIL or not conf.SENDER_PASSWORD:
                tts.speak_error("Email is not configured. Please set up Gmail credentials in the .env file.")
                return True
            
            tts.speak_success("Checking your emails...")
            res = executor.execute("read_emails", count=5)
            tts.speak_success(res.message) if res.ok else tts.speak_error(res.message)
        
        else:
            tts.speak_warning("Command recognized but not implemented.")
        
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        tts.speak_error("An error occurred while executing the command.")
    
    return True

