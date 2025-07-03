# LeetCode Streak Checker - Core Logic
import os
import random
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
import json
from typing import Dict, Optional, List
import requests
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Configuration
token = os.getenv("TELEGRAM_TOKEN")
if not token:
    logger.error("TELEGRAM_TOKEN environment variable is not set!")
    
TELEGRAM_API_URL = f"https://api.telegram.org/bot{token}"

# File to store user data persistently
USERS_FILE = "users.json"

# Store processed message IDs to prevent duplicates
processed_messages = set()

def load_users() -> Dict[str, str]:
    """Load users from JSON file."""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} users from {USERS_FILE}")
                return data
    except Exception as e:
        logger.error(f"Error loading users: {e}")
    return {}

def save_users_to_file() -> None:
    """Save users to JSON file."""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        logger.info(f"Saved {len(users)} users to {USERS_FILE}")
    except Exception as e:
        logger.error(f"Error saving users: {e}")

# Load users from file on startup
users: Dict[str, str] = load_users()

# Enhanced message collections
success_messages = [
    "✅ Beast mode active! You've submitted today. Keep the streak alive! 🔥",
    "🧠 Brains > excuses. You're winning this grind! 💪",
    "📈 Daily effort = future success. Keep going! 🚀",
    "🚀 Streak is intact, captain. Onwards to greatness! ⭐",
    "🔥 Submission detected. Consistency is your superpower! 💯",
    "👊 You're in the 1% who showed up today. Respect! 🏆",
    "🎯 Another day, another problem solved. You're unstoppable! 🌟",
    "💎 Coding diamond in the making. Today's effort counts! ✨"
]

warning_messages = [
    "⚠️ Hey! You haven't submitted on LeetCode today. Clock's ticking! ⏰🔥",
    "🚨 Streak alert! Your coding streak needs attention. Time to code! 💻",
    "⏰ Day's almost over and no submissions yet. Don't break the chain! 🔗",
    "🎯 Missing today's target! Quick, solve something before midnight! 🌙"
]

def get_random_message(message_list: List[str]) -> str:
    """Get a random message from the provided list."""
    return random.choice(message_list)

def get_user_leetcode(chat_id: str) -> Optional[str]:
    """Get LeetCode username for a given chat_id."""
    return users.get(str(chat_id))

def save_user(chat_id: str, leetcode_username: str) -> None:
    """Save user's LeetCode username."""
    users[str(chat_id)] = leetcode_username
    save_users_to_file()
    logger.info(f"Registered user {leetcode_username} with chat_id {chat_id}")

def validate_leetcode_username(username: str) -> bool:
    """Validate if a LeetCode username exists by making a test query."""
    try:
        url = "https://leetcode.com/graphql"
        headers = {
            "Content-Type": "application/json",
            "Referer": f"https://leetcode.com/{username}/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        query = """
        query userProfile($username: String!) {
          matchedUser(username: $username) {
            username
            profile {
              realName
            }
          }
        }
        """

        payload = {
            "query": query,
            "variables": {"username": username}
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("matchedUser") is not None
        return False
    except Exception as e:
        logger.error(f"Error validating username {username}: {e}")
        return False

def has_submitted_today(username: str) -> bool:
    """Check if user has submitted any problem today."""
    try:
        url = "https://leetcode.com/graphql"
        headers = {
            "Content-Type": "application/json",
            "Referer": f"https://leetcode.com/{username}/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        query = """
        query recentSubmissionList($username: String!) {
          recentSubmissionList(username: $username, limit: 10) {
            timestamp
            statusDisplay
            title
            lang
          }
        }
        """

        payload = {
            "query": query,
            "variables": {"username": username}
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code != 200:
            logger.error(f"Failed to fetch data from LeetCode GraphQL for {username}")
            return False

        data = response.json()
        if "errors" in data:
            logger.error(f"GraphQL errors for {username}: {data['errors']}")
            return False

        submissions = data.get("data", {}).get("recentSubmissionList", [])
        if not submissions:
            logger.info(f"No recent submissions found for {username}")
            return False

        today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
        logger.info(f"Checking submissions for {username} on {today}")

        for sub in submissions:
            try:
                sub_time = datetime.fromtimestamp(int(sub["timestamp"]), ZoneInfo("Asia/Kolkata")).date()
                if sub_time == today:
                    logger.info(f"Found submission for {username} on {today}: {sub['title']}")
                    return True
            except Exception as e:
                logger.warning(f"Failed to parse submission timestamp for {username}: {e}")

        logger.info(f"No submissions found for {username} on {today}")
        return False
        
    except Exception as e:
        logger.error(f"Error checking submissions for {username}: {e}")
        return False

def send_telegram_message(chat_id: str, message: str) -> bool:
    """Send a message to Telegram chat."""
    try:
        response = requests.post(
            f"{TELEGRAM_API_URL}/sendMessage", 
            data={
                "chat_id": chat_id, 
                "text": message,
                "parse_mode": "HTML"
            },
            timeout=10
        )
        if response.status_code == 200:
            logger.info(f"Message sent successfully to {chat_id}")
            return True
        else:
            logger.error(f"Failed to send message to {chat_id}: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Telegram send error for {chat_id}: {e}")
        return False

def handle_message(update: dict) -> None:
    """Handle incoming Telegram messages."""
    try:
        message = update.get("message", {})
        chat_id = str(message.get("chat", {}).get("id"))
        text = message.get("text", "").strip()
        username = message.get("from", {}).get("username", "unknown")
        message_id = message.get("message_id")

        if not chat_id or not text:
            logger.warning("Received message without chat_id or text")
            return

        # Check for duplicate messages
        if message_id:
            message_key = f"{chat_id}:{message_id}"
            if message_key in processed_messages:
                logger.info(f"Skipping duplicate message {message_key}")
                return
            processed_messages.add(message_key)
            
            # Keep only recent message IDs (last 1000) to prevent memory issues
            if len(processed_messages) > 1000:
                processed_messages.clear()

        logger.info(f"Received message from {username} ({chat_id}): {text}")

        if text.startswith("/start"):
            welcome_message = """
🚀 <b>Welcome to LeetCode Streak Checker Bot!</b> 

This bot helps you maintain your LeetCode coding streak by:
• Tracking your daily submissions
• Sending motivational messages
• Keeping you accountable

<b>Available Commands:</b>
• /register &lt;username&gt; - Register your LeetCode username
• /check - Check your submission status for today
• /help - Show this help message

<b>Get Started:</b>
Use <code>/register your_leetcode_username</code> to begin tracking your streak!
            """
            send_telegram_message(chat_id, welcome_message)
            return

        if text.startswith("/help"):
            help_message = """
<b>LeetCode Streak Checker Bot - Help</b>

<b>Commands:</b>
• <code>/start</code> - Welcome message and introduction
• <code>/register &lt;username&gt;</code> - Register your LeetCode username
• <code>/check</code> - Check if you've submitted today
• <code>/help</code> - Show this help message

<b>Example:</b>
<code>/register john_doe</code>

<b>Note:</b> Make sure your LeetCode profile is public for the bot to check your submissions.
            """
            send_telegram_message(chat_id, help_message)
            return

        if text.startswith("/register"):
            parts = text.split()
            if len(parts) != 2:
                logger.warning(f"Invalid register command from {chat_id}: {text}")
                send_telegram_message(chat_id, "❌ Please provide your LeetCode username.\n"
                                    "Example: /register johndoe")
                return

            leetcode_username = parts[1]
            logger.info(f"Registration attempt: chat_id={chat_id}, username={leetcode_username}")
            
            # Check if user is already registered
            if str(chat_id) in users:
                current_username = users[str(chat_id)]
                logger.info(f"User {chat_id} already registered with username: {current_username}")
                send_telegram_message(chat_id, f"ℹ️ You're already registered with username: {current_username}\n"
                                    f"To change username, contact support or re-register.")
                return
            
            # Validate username first
            logger.info(f"Validating LeetCode username: {leetcode_username}")
            if not validate_leetcode_username(leetcode_username):
                logger.warning(f"Username validation failed for: {leetcode_username}")
                send_telegram_message(chat_id, f"❌ LeetCode username '{leetcode_username}' not found or profile is private.\n"
                                    "Please check your username and make sure your profile is public.")
                return
                
            save_user(chat_id, leetcode_username)
            logger.info(f"Successfully registered user: {chat_id} -> {leetcode_username}")
            send_telegram_message(chat_id, f"✅ Successfully registered with LeetCode username: {leetcode_username}\n"
                                f"🎯 You'll now receive daily streak reminders at 8:00 PM IST!")
            return

        if text.startswith("/check"):
            leetcode_username = get_user_leetcode(chat_id)
            if not leetcode_username:
                send_telegram_message(chat_id, "❌ You haven't registered yet!\n"
                                    "Use /register <your_leetcode_username> to get started.")
                return

            send_telegram_message(chat_id, "🔍 Checking your submissions... Please wait.")
            
            if has_submitted_today(leetcode_username):
                send_telegram_message(chat_id, get_random_message(success_messages))
            else:
                send_telegram_message(chat_id, get_random_message(warning_messages))
            return
            
        # Handle unknown commands
        send_telegram_message(chat_id, "❓ Unknown command. Use /help to see available commands.")
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        if 'chat_id' in locals():
            send_telegram_message(chat_id, "❌ Sorry, something went wrong. Please try again later.")

def handle_webhook(request_data: dict) -> None:
    """Handle incoming webhook from Telegram."""
    if "message" in request_data:
        handle_message(request_data)

def set_webhook(webhook_url: str) -> bool:
    """Set the webhook URL for the Telegram bot."""
    try:
        logger.info(f"Setting webhook to: {webhook_url}")
        response = requests.post(f"{TELEGRAM_API_URL}/setWebhook", data={"url": webhook_url}, timeout=10)
        if response.status_code == 200:
            logger.info("Webhook set successfully")
            return True
        else:
            logger.error(f"Failed to set webhook: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        return False

def check_all_users() -> None:
    """Check submissions for all registered users."""
    if not users:
        logger.info("No users registered yet")
        return
        
    logger.info(f"Checking submissions for {len(users)} users")
    
    for chat_id, username in users.items():
        try:
            logger.info(f"Checking user {username} ({chat_id})")
            if has_submitted_today(username):
                send_telegram_message(chat_id, get_random_message(success_messages))
            else:
                send_telegram_message(chat_id, get_random_message(warning_messages))
            logger.info(f"Checked streak for {username} on {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            logger.error(f"Error checking user {username}: {e}")

if __name__ == "__main__":
    # If running as a script, check all users (for cron job compatibility)
    logger.info("Running manual check for all users")
    check_all_users()