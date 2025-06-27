# ⚡ LeetCode Streak Checker Bot 🔔

> A daily reminder bot that keeps your LeetCode streak alive—or roasts you if you slack.

This GitHub Action checks if you've submitted any problem on LeetCode today. If you haven't, it sends a Telegram message at **10:45 PM IST** to guilt-trip you into staying consistent.

If you have submitted? You get some motivational praise instead. Because you earned it.

---

## 🛠 Features

✅ Uses LeetCode’s official GraphQL API  
✅ Detects **any submission** made today  
✅ Sends alerts to your **Telegram account**  
✅ Runs every day automatically via GitHub Actions  
✅ Completely customizable messages  
✅ Works without exposing your tokens or usernames publicly

---

## 📦 Tech Stack

- Python 3.10
- GitHub Actions
- LeetCode GraphQL API
- Telegram Bot API

---

## 🧪 How It Works

1. GitHub Action runs every day at **10:00 PM IST**
2. Python script checks your 5 most recent submissions
3. If a submission is found for today:
   - 🎉 Sends motivational message
4. If no submission found:
   - 🔔 Sends warning to fix your streak ASAP

---

## 🚀 Setup Instructions

1. **Fork this repo**

2. **Create a Telegram Bot** via [@BotFather](https://t.me/BotFather)
   - Save the **bot token**

3. **Get your Telegram User ID**
   - Use [@userinfobot](https://t.me/userinfobot) to find your `chat_id`

4. **Add GitHub Secrets** to your repo:
   - `TELEGRAM_TOKEN` = your bot token
   - `CHAT_ID` = your Telegram user ID
   - `LEETCODE_USERNAME` = your LeetCode handle (e.g., `utkarshrajput1583`)

5. ✅ You’re done. The bot runs every day. You can also trigger it manually via GitHub Actions → "Run workflow".

---

## 🧠 Example Telegram Messages

**If you haven’t submitted:**
You haven’t submitted on LeetCode today. Clock’s ticking! ⏰🔥
**If you have submitted:**
✅ Beast mode active. You’ve submitted today. Keep the streak alive! 🔥
(or one of many random motivational messages)

---

## 🤖 Customization Ideas

- Add streak counters and badges
- Track Daily Challenge only
- Push leaderboard stats for friend groups
- Add memes, stickers, or GPT-generated messages

---

## 🧍‍♂️ Author

Made by [@utkarshrajputt](https://github.com/utkarshrajputt) to stay accountable and build cool automation.

Feel free to fork and tweak. Just don’t break your streak. 😤

---

## 🏁 License

MIT – Go nuts, just don’t be evil.
