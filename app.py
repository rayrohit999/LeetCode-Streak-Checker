from flask import Flask, request, jsonify
import os
import logging
import threading
import time
import schedule
from datetime import datetime, time as dtime
from typing import List
from zoneinfo import ZoneInfo
from streak_check import handle_webhook, set_webhook, check_all_users, get_user_leetcode, users

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Timezone configuration
IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")

# Read desired IST check times from env (comma-separated HH:MM)
# Defaults: 09:00, 13:30, 18:00, 20:00 (IST)
CHECK_TIMES_IST = os.getenv("CHECK_TIMES_IST", "09:00,13:30,18:00,20:00")

def _parse_hhmm(value: str) -> tuple[int, int]:
    parts = value.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid time format '{value}', expected HH:MM")
    h, m = int(parts[0]), int(parts[1])
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError(f"Invalid time '{value}'")
    return h, m

def ist_to_utc_hhmm(ist_hhmm: str) -> str:
    """Convert an IST HH:MM string to a UTC HH:MM string for scheduling.
    Uses today's date; only the HH:MM is returned for schedule.every().day.at()."""
    h, m = _parse_hhmm(ist_hhmm)
    # Use an arbitrary date (today) for conversion
    now_utc = datetime.now(UTC)
    # Construct IST datetime for today with given hour:minute
    ist_dt_today = datetime(year=now_utc.year, month=now_utc.month, day=now_utc.day, hour=h, minute=m, tzinfo=IST)
    # Convert to UTC time
    utc_dt = ist_dt_today.astimezone(UTC)
    return utc_dt.strftime("%H:%M")

def get_scheduled_times_pairs() -> List[dict]:
    """Return list of dicts with IST/UTC time strings for display/logging."""
    pairs = []
    for t in [t.strip() for t in CHECK_TIMES_IST.split(',') if t.strip()]:
        try:
            utc_t = ist_to_utc_hhmm(t)
            pairs.append({"ist": t, "utc": utc_t})
        except Exception as e:
            logger.error(f"Skipping invalid time '{t}': {e}")
    return pairs

# Scheduler setup
def scheduled_streak_check():
    """Run scheduled check for all users."""
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"🕐 Running scheduled streak check at {current_time}")
        check_all_users()
        logger.info("✅ Scheduled streak check completed")
    except Exception as e:
        logger.error(f"❌ Error in scheduled check: {e}")

def run_scheduler():
    """Run the scheduler in a separate thread with IST-aware times (converted to UTC)."""
    # Clear any pre-existing jobs to avoid duplicates on restarts
    schedule.clear()

    times_pairs = get_scheduled_times_pairs()
    if not times_pairs:
        # Fallback to 20:00 IST -> 14:30 UTC
        times_pairs = [{"ist": "20:00", "utc": "14:30"}]

    for pair in times_pairs:
        schedule.every().day.at(pair["utc"]).do(scheduled_streak_check)
        logger.info(f"⏰ Scheduled daily streak check at {pair['ist']} IST ({pair['utc']} UTC)")

    logger.info("📅 Scheduler started with IST-aware timings: " + ", ".join([p['ist'] for p in times_pairs]))

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            time.sleep(60)

# Start scheduler in background thread only if not in debug mode or main process
if not os.environ.get('WERKZEUG_RUN_MAIN'):
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("🔄 Scheduler thread started")

# Basic security headers
@app.after_request
def after_request(response):
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('X-Frame-Options', 'DENY')
    response.headers.add('X-XSS-Protection', '1; mode=block')
    return response

@app.route('/')
def home():
    """Home page with API information and health status."""
    return jsonify({
        "message": "LeetCode Streak Checker Bot API",
        "version": "1.0.0",
        "features": {
            "automatic_daily_checks_ist": [p['ist'] for p in get_scheduled_times_pairs()],
            "manual_commands": "Available via Telegram",
            "webhook_support": "Real-time responses"
        },
        "endpoints": {
            "/": "GET - API information and health check",
            "/webhook": "POST - Handle Telegram webhook",
            "/set_webhook": "POST - Set webhook URL",
            "/health": "GET - Health check endpoint",
            "/stats": "GET - Bot statistics",
            "/manual_check": "POST - Manually trigger check for all users",
            "/users": "GET - Detailed user information"
        },
        "status": "running",
        "scheduler": "active",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check if TELEGRAM_TOKEN is set
        token_configured = bool(os.getenv("TELEGRAM_TOKEN"))
        
        # Check if scheduler is running
        scheduler_jobs = len(schedule.jobs)
        
        return jsonify({
            "status": "healthy",
            "telegram_token_configured": token_configured,
            "registered_users": len(users),
            "scheduler_active": scheduler_jobs > 0,
            "scheduled_jobs": scheduler_jobs,
            "next_scheduled_run_utc": str(schedule.next_run()) if schedule.jobs else "No jobs scheduled",
            "next_scheduled_run_ist": (schedule.next_run().replace(tzinfo=UTC).astimezone(IST).strftime('%Y-%m-%d %H:%M:%S IST') if schedule.jobs else "No jobs scheduled"),
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/stats')
def get_stats():
    """Get bot statistics."""
    try:
        next_run = str(schedule.next_run()) if schedule.jobs else "No scheduled jobs"
        
        return jsonify({
            "total_users": len(users),
            "registered_users": list(users.keys()),
            "scheduler_status": "active" if schedule.jobs else "inactive",
            "scheduled_jobs": len(schedule.jobs),
            "next_scheduled_check_utc": next_run,
            "next_scheduled_check_ist": (schedule.next_run().replace(tzinfo=UTC).astimezone(IST).strftime('%Y-%m-%d %H:%M:%S IST') if schedule.jobs else "No scheduled jobs"),
            "daily_check_times_ist": [p['ist'] for p in get_scheduled_times_pairs()],
            "bot_uptime": datetime.now().isoformat(),
            "status": "active"
        }), 200
    except Exception as e:
        logger.error(f"Stats endpoint error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook requests from Telegram."""
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                logger.warning("Received empty webhook data")
                return jsonify({"status": "error", "message": "No data received"}), 400
            
            # Log webhook data but don't include sensitive info
            update_id = data.get('update_id', 'unknown')
            logger.info(f"Processing webhook update_id: {update_id}")
            
            handle_webhook(data)
            return jsonify({"status": "success"}), 200
        except Exception as e:
            logger.error(f"Webhook handling error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error", "message": "Method not allowed"}), 405

@app.route('/set_webhook', methods=['POST'])
def setup_webhook():
    """Set up the webhook URL for the Telegram bot."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        webhook_url = data.get('webhook_url')
        if not webhook_url:
            return jsonify({"status": "error", "message": "webhook_url is required"}), 400
        
        # Validate webhook URL format
        if not webhook_url.startswith(('http://', 'https://')):
            return jsonify({"status": "error", "message": "Invalid webhook URL format"}), 400
            
        logger.info(f"Setting webhook to: {webhook_url}")
        success = set_webhook(webhook_url)
        if success:
            logger.info("Webhook set successfully")
            return jsonify({"status": "success", "message": "Webhook set successfully"}), 200
        else:
            logger.error("Failed to set webhook")
            return jsonify({"status": "error", "message": "Failed to set webhook"}), 500
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/manual_check', methods=['POST'])
def manual_check():
    """Manually trigger streak check for all users."""
    try:
        logger.info("Manual check triggered via API")
        check_all_users()
        return jsonify({
            "status": "success", 
            "message": f"Manual check completed for {len(users)} users",
            "users_checked": len(users),
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Manual check error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/scheduler_status')
def scheduler_status():
    """Get detailed scheduler information."""
    try:
        jobs_info = []
        for job in schedule.jobs:
            next_run_utc = job.next_run  # naive datetime in server local time (UTC on Render)
            next_run_ist = None
            if next_run_utc:
                try:
                    next_run_ist = next_run_utc.replace(tzinfo=UTC).astimezone(IST).strftime('%Y-%m-%d %H:%M:%S IST')
                except Exception:
                    next_run_ist = None
            jobs_info.append({
                "job": str(job.job_func.__name__),
                "next_run_utc": str(next_run_utc),
                "next_run_ist": next_run_ist,
                "interval": str(job.interval),
                "unit": job.unit
            })

        next_run_global_utc = str(schedule.next_run()) if schedule.jobs else None
        next_run_global_ist = None
        if schedule.jobs and schedule.next_run():
            try:
                next_run_global_ist = schedule.next_run().replace(tzinfo=UTC).astimezone(IST).strftime('%Y-%m-%d %H:%M:%S IST')
            except Exception:
                next_run_global_ist = None

        return jsonify({
            "scheduler_active": len(schedule.jobs) > 0,
            "total_jobs": len(schedule.jobs),
            "jobs": jobs_info,
            "next_run_utc": next_run_global_utc,
            "next_run_ist": next_run_global_ist,
            "current_time_utc": datetime.now(UTC).isoformat(),
            "current_time_ist": datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST'),
            "configured_times_ist": [p['ist'] for p in get_scheduled_times_pairs()],
            "configured_times_utc": [p['utc'] for p in get_scheduled_times_pairs()],
        }), 200
    except Exception as e:
        logger.error(f"Scheduler status error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/users')
def get_users():
    """Get detailed user information for debugging."""
    try:
        user_details = []
        for chat_id, username in users.items():
            user_details.append({
                "chat_id": chat_id,
                "leetcode_username": username,
                "registered_at": "Unknown"  # We could add timestamps in future
            })
        
        return jsonify({
            "total_users": len(users),
            "users": user_details,
            "raw_users_data": users,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Users endpoint error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"status": "error", "message": "Internal server error"}), 500

if __name__ == '__main__':
    # Check if required environment variables are set
    if not os.getenv("TELEGRAM_TOKEN"):
        logger.error("TELEGRAM_TOKEN environment variable is not set!")
        print("❌ Error: TELEGRAM_TOKEN environment variable is required!")
        exit(1)
    
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask app on http://localhost:{port}")
    logger.info(f"Debug mode: {debug_mode}")
    logger.info(f"Registered users: {len(users)}")
    logger.info(f"📅 Automatic daily checks (IST): {', '.join([p['ist'] for p in get_scheduled_times_pairs()])}")
    
    print(f"🚀 Starting LeetCode Streak Checker Bot API on http://localhost:{port}")
    print(f"📊 Currently tracking {len(users)} users")
    print(f"⏰ Daily automatic checks (IST): {', '.join([p['ist'] for p in get_scheduled_times_pairs()])}")
    print(f"🔄 Scheduler: {'Active' if schedule.jobs else 'Inactive'}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=debug_mode)