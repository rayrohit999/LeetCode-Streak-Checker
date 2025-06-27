import time
import threading
import schedule
from datetime import datetime
from zoneinfo import ZoneInfo
from streak_check import *

def scheduled_check():
    """Run the check for all users and log the execution."""
    print(f"🕐 Running scheduled check at {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}")
    check_all_users()
    print("✅ Scheduled check completed")

def run_scheduler():
    """Run the scheduler in a separate thread."""
    # Schedule daily check at 8:00 PM IST
    schedule.every().day.at("19:30").do(scheduled_check)
    
    print("📅 Scheduler started. Daily checks scheduled at 8:00 PM IST")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except Exception as e:
            print(f"❌ Scheduler error: {e}")
            time.sleep(60)

def get_updates(offset=None):
    """Get updates from Telegram."""
    url = f"{TELEGRAM_API_URL}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    
    try:
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def run_bot():
    """Run the bot continuously."""
    print("🤖 Bot started...")
    offset = None
    
    while True:
        try:
            updates = get_updates(offset)
            if updates and updates.get("ok"):
                for update in updates["result"]:
                    handle_message(update)
                    offset = update["update_id"] + 1
            time.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Bot stopped.")
            break
        except Exception as e:
            print(f"❌ Bot error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Start scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Run the bot in the main thread
    run_bot()