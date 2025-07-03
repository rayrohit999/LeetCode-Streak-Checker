# 🚀 Step-by-Step Deployment Guide

## 📋 **Pre-Deployment Checklist**
✅ Bot tested and working locally  
✅ All features functional (/start, /register, /check, /help)  
✅ Automatic scheduling implemented  
✅ Clean file structure ready  
✅ Environment variables identified  

---

## 🔄 **Step 1: Upload to GitHub**

### Option A: Using GitHub Desktop (Recommended)
1. **Download GitHub Desktop**: https://desktop.github.com/
2. **Install and sign in** with your GitHub account
3. **Create new repository**:
   - Click "Create a New Repository on your hard drive"
   - Name: `leetcode-streak-checker`
   - Description: `Telegram bot to track LeetCode daily streaks`
   - Make it Public
   - Choose your current folder location
4. **Add files**: Copy all 7 files to the repository folder
5. **Commit and push**: 
   - Write commit message: "Initial commit - LeetCode Streak Checker Bot"
   - Click "Commit to main"
   - Click "Publish repository"

### Option B: Using Command Line
```bash
git init
git add .
git commit -m "Initial commit - LeetCode Streak Checker Bot"
git branch -M main
git remote add origin https://github.com/yourusername/leetcode-streak-checker.git
git push -u origin main
```

---

## 🌐 **Step 2: Deploy to Render**

### 2.1 Create Render Account
1. Go to **https://render.com**
2. **Sign up** using your GitHub account
3. **Authorize Render** to access your repositories

### 2.2 Create Web Service
1. **Click "New"** → **"Web Service"**
2. **Connect Repository**: Select `leetcode-streak-checker`
3. **Configure Settings**:
   ```
   Name: leetcode-streak-checker
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python app.py
   ```

### 2.3 Set Environment Variables
In the **Environment** section, add:
```
TELEGRAM_TOKEN = 7548755184:AAEprqJKX2urZrxLP7nC-Qt9li8WumSuKQE
PORT = 10000
DEBUG = False
```

### 2.4 Deploy
1. **Click "Create Web Service"**
2. **Wait for deployment** (5-10 minutes)
3. **Note your app URL**: `https://your-app-name.onrender.com`

---

## 🔗 **Step 3: Set Webhook**

After deployment, set the webhook using your live URL:

### Method 1: Using curl (Command Line)
```bash
curl -X POST https://your-app-name.onrender.com/set_webhook \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "https://your-app-name.onrender.com/webhook"}'
```

### Method 2: Using PowerShell
```powershell
$body = @{
    webhook_url = "https://your-app-name.onrender.com/webhook"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://your-app-name.onrender.com/set_webhook" -Method POST -Body $body -ContentType "application/json"
```

### Method 3: Using Postman/Insomnia
```
POST https://your-app-name.onrender.com/set_webhook
Content-Type: application/json

{
  "webhook_url": "https://your-app-name.onrender.com/webhook"
}
```

---

## ✅ **Step 4: Test Your Live Bot**

1. **Health Check**: Visit `https://your-app-name.onrender.com/health`
2. **Telegram Test**: Send `/start` to your bot
3. **Register Test**: Send `/register your_leetcode_username`
4. **Check Test**: Send `/check`

---

## 📊 **Step 5: Monitor Your Bot**

### Available Monitoring URLs:
- **Health**: `https://your-app-name.onrender.com/health`
- **Stats**: `https://your-app-name.onrender.com/stats`
- **Scheduler**: `https://your-app-name.onrender.com/scheduler_status`

### Render Dashboard:
- **Logs**: View real-time application logs
- **Metrics**: Monitor CPU, memory usage
- **Settings**: Update environment variables

---

## 🎉 **Congratulations!**

Your LeetCode Streak Checker Bot is now:
- ✅ **Live on the internet**
- ✅ **Automatically checking streaks daily at 8PM IST**
- ✅ **Responding to user commands instantly**
- ✅ **Scalable and production-ready**

### 🔥 **Share Your Bot:**
- **Bot Username**: @leetcode_streak_cheacker_bot
- **Bot Link**: https://t.me/leetcode_streak_cheacker_bot

---

## 🛠 **Need Help?**

### Common Issues:
1. **Webhook not working**: Check environment variables
2. **Bot not responding**: Verify webhook URL is set correctly
3. **Daily checks not running**: Check scheduler status endpoint

### Support Resources:
- **Render Docs**: https://render.com/docs
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **Your Bot Status**: Check `/health` endpoint

**Ready to deploy? Let's go! 🚀**
