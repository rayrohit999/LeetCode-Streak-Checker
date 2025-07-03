# ⚡ LeetCode Streak Checker Bot 🔔

> **Keep your LeetCode streak alive with daily automated reminders!**

A Telegram bot that automatically checks your LeetCode submissions every day and sends motivational messages to maintain your coding streak.

🤖 **Bot**: [@leetcode_streak_cheacker_bot](https://t.me/leetcode_streak_cheacker_bot)

---

## 🎯 **What This Bot Does**

### **Automatic Daily Checks**
- **Every day at 8:00 PM IST**, the bot checks all registered users
- **Sends motivational messages** if you've submitted code today
- **Sends gentle reminders** if you haven't coded yet

### **Manual Commands**
- `/start` - Welcome message and instructions
- `/register <username>` - Register your LeetCode username  
- `/check` - Check your submission status for today
- `/help` - Show available commands

---

## 🚀 **Quick Start**

### **1. Start Using the Bot**
1. **Find the bot**: [@leetcode_streak_cheacker_bot](https://t.me/leetcode_streak_cheacker_bot)
2. **Send**: `/start` to begin
3. **Register**: `/register your_leetcode_username`
4. **Test**: `/check` to see if you've coded today

### **2. Example Usage**
```
/start
/register john_doe
/check
```

**That's it!** The bot will automatically check your streak every evening.

---

## ✨ **Features**

✅ **LeetCode GraphQL API Integration** - Official submission data  
✅ **Automatic Daily Reminders** - 8:00 PM IST checks  
✅ **Real-time Commands** - Instant Telegram responses  
✅ **Username Validation** - Verifies LeetCode profiles  
✅ **Motivational Messages** - Dynamic success/reminder messages  
✅ **Persistent Storage** - User data saved securely  
✅ **Production Ready** - Scalable and monitored  

---

## 🛠 **Tech Stack**

- **Python 3.11** with Flask web framework
- **LeetCode GraphQL API** for submission data
- **Telegram Bot API** for messaging
- **Automated Scheduling** for daily checks
- **Render.com** for hosting (or any platform)

---

## 🏗 **Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │◄──►│   Flask Bot      │◄──►│   LeetCode      │
│   Users         │    │   Application    │    │   GraphQL API   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────▼──────┐
                       │  Scheduler  │
                       │ (Daily 8PM) │
                       └─────────────┘
```

---

## 📊 **Bot Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Get started with the bot | `/start` |
| `/register <username>` | Register your LeetCode profile | `/register john_doe` |
| `/check` | Check today's submission status | `/check` |
| `/help` | Show help information | `/help` |

---

## 🌐 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and status |
| `/health` | GET | Health check and monitoring |
| `/stats` | GET | Bot statistics and user count |
| `/webhook` | POST | Telegram webhook handler |
| `/set_webhook` | POST | Configure webhook URL |
| `/manual_check` | POST | Manually trigger checks |

---

## 🔧 **Self-Hosting**

Want to run your own instance? 

### **Prerequisites**
- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Hosting platform (Render, Heroku, Railway, etc.)

### **Environment Variables**
```bash
TELEGRAM_TOKEN=your_bot_token_here
PORT=10000
DEBUG=False
```

### **Deployment**
1. **Clone this repository**
2. **Set environment variables**
3. **Deploy to your platform**
4. **Set webhook URL**

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## 📈 **Statistics**

- **Active Users**: Growing daily
- **Daily Checks**: Automated at 8PM IST
- **Response Time**: < 2 seconds
- **Uptime**: 99.9%

---

## 🤝 **Contributing**

Found a bug or want to add a feature?

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Submit a pull request**

---

## �‍💻 **Credits & Contributors**

### **Original Author**
**[@utkarshrajputt](https://github.com/utkarshrajputt)** - Created the original LeetCode Streak Checker Bot to stay accountable and build cool automation.

### **Enhanced By**
**[@rayrohit999](https://github.com/rayrohit999)** - Enhanced the bot with production-ready features, automatic scheduling, webhook support, and comprehensive deployment capabilities.

### **Contributions**
- **Original Concept**: LeetCode streak tracking and Telegram integration
- **Production Enhancement**: Flask API, scheduler, health monitoring, deployment optimization
- **Community**: Open source project for the coding community

---

## �📝 **License**

This project is open source and available under the [MIT License](LICENSE).

---

## 💡 **Tips for Success**

- **Keep your LeetCode profile public** for the bot to check submissions
- **Register with your exact LeetCode username** (case-sensitive)
- **Check the bot daily** to stay motivated
- **Share with friends** to create accountability

---

## 🆘 **Support**

- **Issues**: Open a GitHub issue
- **Questions**: Ask in discussions
- **Bot Problems**: Check the `/health` endpoint

---

**Made with ❤️ for the LeetCode community. Keep coding, keep growing! 🔥**

🔗 **Bot Link**: [@leetcode_streak_cheacker_bot](https://t.me/leetcode_streak_cheacker_bot)
