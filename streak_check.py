# amazonq-ignore-next-lineimport requests
import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo
import json
from typing import Dict, Optional
import requests
token = "7548755184:AAEprqJKX2urZrxLP7nC-Qt9li8WumSuKQE"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{token}"

# File to store user data persistently
USERS_FILE = "users.json"

def load_users() -> Dict[str, str]:
    """Load users from JSON file."""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading users: {e}")
    return {}

def save_users_to_file() -> None:
    """Save users to JSON file."""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving users: {e}")

# Load users from file on startup
users: Dict[str, str] = load_users()

success_messages = [
    "✅ Beast mode active. You've submitted today. Keep the streak alive! 🔥",
    "🧠 Brains > excuses. You're winning this grind.",
    "📈 Daily effort = future flex. Keep going!",
    "🚀 Streak is intact, captain. Onwards to greatness!",
    "🔥 Submission detected. Consistency is sexy.",
    "👊 You're in the 1% who showed up. Respect!"
]

warning_message = "⚠️ Hey! You haven't submitted on LeetCode today. Clock's ticking! ⏰🔥"

def get_user_leetcode(chat_id: str) -> Optional[str]:
    """Get LeetCode username for a given chat_id."""
    return users.get(str(chat_id))

def save_user(chat_id: str, leetcode_username: str) -> None:
    """Save user's LeetCode username."""
    users[str(chat_id)] = leetcode_username
    save_users_to_file()

def has_submitted_today(username):
    url = "https://leetcode.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{username}/",
        "User-Agent": "Mozilla/5.0"
    }

    query = """
    query recentSubmissionList($username: String!) {
      recentSubmissionList(username: $username, limit: 5) {
        timestamp
        statusDisplay
        title
      }
    }
    """

    payload = {
        "query": query,
        "variables": {"username": username}
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        print("❌ Failed to fetch data from LeetCode GraphQL.")
        return False

    submissions = response.json()["data"]["recentSubmissionList"]
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()

    for sub in submissions:
        try:
            sub_time = datetime.fromtimestamp(int(sub["timestamp"]), ZoneInfo("Asia/Kolkata")).date()
            if sub_time == today:
                return True
        except Exception as e:
            print(f"⚠️ Failed to parse submission timestamp: {e}")

    return False

def send_telegram_message(chat_id: str, message: str):
    try:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", data={"chat_id": chat_id, "text": message})
    except Exception as e:
        print(f"❌ Telegram send error: {e}")

def handle_message(update: dict) -> None:
    """Handle incoming Telegram messages."""
    message = update.get("message", {})
    chat_id = str(message.get("chat", {}).get("id"))
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return

    if text.startswith("/start"):
        send_telegram_message(chat_id, "Welcome to LeetCode Streak Checker Bot! 🚀\n\n"
                            "To register, use the command:\n"
                            "/register <your_leetcode_username>\n\n"
                            "To check your streak:\n"
                            "/check")
        return

    if text.startswith("/register"):
        parts = text.split()
        if len(parts) != 2:
            send_telegram_message(chat_id, "❌ Please provide your LeetCode username.\n"
                                "Example: /register johndoe")
            return

        leetcode_username = parts[1]
        save_user(chat_id, leetcode_username)
        send_telegram_message(chat_id, f"✅ Successfully registered with LeetCode username: {leetcode_username}")
        return

    if text.startswith("/check"):
        leetcode_username = get_user_leetcode(chat_id)
        if not leetcode_username:
            send_telegram_message(chat_id, "❌ You haven't registered yet!\n"
                                "Use /register <your_leetcode_username> to get started.")
            return

        if has_submitted_today(leetcode_username):
            send_telegram_message(chat_id, random.choice(success_messages))
        else:
            send_telegram_message(chat_id, warning_message)
        return

def handle_webhook(request_data: dict) -> None:
    """Handle incoming webhook from Telegram."""
    if "message" in request_data:
        handle_message(request_data)

def set_webhook(webhook_url: str) -> bool:
    """Set the webhook URL for the Telegram bot."""
    try:
        response = requests.post(f"{TELEGRAM_API_URL}/setWebhook", data={"url": webhook_url})
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Failed to set webhook: {e}")
        return False

# For backward compatibility with the original cron job
def check_all_users():
    """Check submissions for all registered users."""
    for chat_id, username in users.items():
        if has_submitted_today(username):
            send_telegram_message(chat_id, random.choice(success_messages))
        else:
            send_telegram_message(chat_id, warning_message)
        print(f"Checked streak for {username} on {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # If running as a script, check all users (for cron job compatibility)
    check_all_users()