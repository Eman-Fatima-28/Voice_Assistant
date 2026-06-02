⚠️ BEFORE RUN - CRITICAL REPLACEMENTS

🔑 STEP 1: Edit .env File
Create .env file in project root and replace these values:

env
# ===== REPLACE WITH YOUR REAL EMAIL =====
SENDER_EMAIL=REPLACE_WITH_YOUR_GMAIL@gmail.com
SENDER_PASSWORD=REPLACE_WITH_APP_PASSWORD

# ===== REPLACE WITH YOUR API KEYS =====
WEATHER_API_KEY=REPLACE_WITH_OPENWEATHER_API_KEY
NEWS_API_KEY=REPLACE_WITH_NEWSAPI_KEY

# ===== CUSTOMIZE THESE (Optional) =====
DEFAULT_CITY=REPLACE_WITH_YOUR_CITY
DEFAULT_NEWS_CATEGORY=technology
📝 WHERE TO GET REAL VALUES:
1. Gmail App Password
🔗 URL: https://myaccount.google.com/apppasswords

Steps:

Enable 2-Factor Authentication on your Google Account
Go to App Passwords page
Select "Mail" → "Windows Computer"
Click "Generate"
Copy the 16-character password (looks like: abcd efgh ijkl mnop)
Paste in .env:
env
   SENDER_EMAIL=your.actual.email@gmail.com
   SENDER_PASSWORD=abcd efgh ijkl mnop
⚠️ Important:

DON'T use your regular Gmail password
MUST use App Password (16 characters with spaces)
Keep this password secret!
2. OpenWeather API Key (Free)
🔗 URL: https://openweathermap.org/api

Steps:

Sign up for free account
Go to "API Keys" section
Copy your API key (looks like: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6)
Paste in .env:
env
   WEATHER_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
Free Tier Limits:

✅ 1,000 API calls per day
✅ 60 calls per minute
✅ Current weather + 5-day forecast
3. NewsAPI Key (Free)
🔗 URL: https://newsapi.org/register

Steps:

Sign up for free account
Copy your API key from dashboard (looks like: k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6)
Paste in .env:
env
   NEWS_API_KEY=k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
Free Tier Limits:

✅ 100 requests per day
✅ Articles from last 30 days
⚠️ Development only (not for production)
4. Default City
Replace with your actual city:

env
DEFAULT_CITY=New York
# or
DEFAULT_CITY=London
# or
DEFAULT_CITY=Tokyo
Valid cities: Any major city name recognized by OpenWeatherMap

🎯 COMPLETE .env EXAMPLE (With Real Values)
env
# ===== EMAIL CONFIGURATION =====
SENDER_EMAIL=johndoe@gmail.com
SENDER_PASSWORD=wxyz abcd efgh ijkl

# ===== API KEYS =====
WEATHER_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
NEWS_API_KEY=k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6

# ===== DEFAULTS =====
DEFAULT_CITY=New York
DEFAULT_NEWS_CATEGORY=technology
⚠️ OPTIONAL: Skip Features You Don't Need
If you don't want certain features, leave fields EMPTY:

Skip Email Features:
env
SENDER_EMAIL=
SENDER_PASSWORD=
Result: Email commands will show "Email not configured"

Skip Weather Features:
env
WEATHER_API_KEY=
Result: Weather commands will show "Weather service unavailable"

Skip News Features:
env
NEWS_API_KEY=
Result: News commands will show "News service unavailable"

✅ VERIFY YOUR CONFIGURATION
After editing .env, run this test:

bash
python -c "from config import Config; Config.validate()"
Expected Output:

# If all configured:
[No warnings - silent success]

# If some missing:
⚠️  Email not configured (email features disabled)
⚠️  Weather API key missing (weather features disabled)
⚠️  News API key missing (news features disabled)
💡 Edit .env file to enable all features
🚫 COMMON MISTAKES TO AVOID
❌ Mistake 1: Using regular Gmail password
env
SENDER_PASSWORD=MyRegularPassword123  # ❌ WRONG
✅ Correct: Use 16-character App Password

env
SENDER_PASSWORD=abcd efgh ijkl mnop  # ✅ CORRECT
❌ Mistake 2: Adding quotes around values
env
SENDER_EMAIL="johndoe@gmail.com"  # ❌ WRONG
WEATHER_API_KEY='a1b2c3d4e5f6'    # ❌ WRONG
✅ Correct: No quotes needed

env
SENDER_EMAIL=johndoe@gmail.com    # ✅ CORRECT
WEATHER_API_KEY=a1b2c3d4e5f6      # ✅ CORRECT
❌ Mistake 3: Spaces around equals sign
env
SENDER_EMAIL = johndoe@gmail.com  # ❌ WRONG
✅ Correct: No spaces around =

env
SENDER_EMAIL=johndoe@gmail.com    # ✅ CORRECT
❌ Mistake 4: Forgetting to create .env file
❌ Editing example.env or config.py
✅ Create NEW file named exactly .env
❌ Mistake 5: Wrong file location
voice-assistant/
  ├── modules/
  │   └── .env        # ❌ WRONG LOCATION
  └── .env            # ✅ CORRECT (project root)
🔒 SECURITY WARNING
⚠️ NEVER SHARE YOUR .env FILE!

It contains sensitive credentials:

❌ Don't commit to Git
❌ Don't share in screenshots
❌ Don't upload to public repositories
✅ Add .env to .gitignore
📋 QUICK CHECKLIST BEFORE RUNNING
 .env file created in project root
 SENDER_EMAIL replaced with real Gmail address
 SENDER_PASSWORD replaced with 16-char App Password
 WEATHER_API_KEY replaced with OpenWeather API key
 NEWS_API_KEY replaced with NewsAPI key
 DEFAULT_CITY set to your city
 No quotes around values
 No spaces around = signs
 File saved as .env (not .env.txt)
 Configuration verified: python -c "from config import Config; Config.validate()"
✅ AFTER REPLACING VALUES
You're ready to run:

bash
python main.py
🆘 STILL STUCK?
Test individual components:
bash
# Test email config
python -c "from config import Config; print(f'Email: {Config.SENDER_EMAIL}')"

# Test API keys
python -c "from config import Config; print(f'Weather: {Config.WEATHER_API_KEY[:10]}...')"

# Test full config
python -c "from config import Config; Config.validate()"
Common errors:
"FileNotFoundError: .env" → Create .env file in project root

"Email features disabled" → Check SENDER_EMAIL and SENDER_PASSWORD are set

"Authentication failed" → Use App Password, not regular password


