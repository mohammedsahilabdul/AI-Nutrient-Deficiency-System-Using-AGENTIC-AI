# 🚀 Groq Setup Guide - FREE AI API

## What is Groq?

Groq provides **free, fast AI API** without any credit card required!

- ✅ **100% Free** - No credit card needed
- ✅ **Super Fast** - 10x faster than alternatives  
- ✅ **Unlimited** - No strict rate limits
- ✅ **Powerful Models** - Mixtral, Llama 2, etc.

---

## 📋 Quick Setup (2 minutes)

### Step 1: Sign Up (Free)
Go to: **https://console.groq.com/keys**

1. Click "Sign Up" (or continue with Google/GitHub)
2. Create account (takes 30 seconds)

### Step 2: Get API Key
1. Go to: https://console.groq.com/keys
2. Click "Create API Key"
3. Copy the key (looks like: `gsk_...`)

### Step 3: Configure Your Project

**Option A: Edit .env file**
```env
GROQ_API_KEY=gsk_your_key_here
USE_GROQ=true
```

**Option B: Copy from example**
```bash
cp .env.example .env
# Edit .env and paste your Groq API key
```

### Step 4: Run Server
```bash
python run_server.py
```

You should see:
```
✓ Initialized Groq LLM (Free & Fast!)
📍 Local URL: http://127.0.0.1:8000
```

---

## ✅ Verification

### Check Groq is Working
```bash
python test_setup.py
```

Should show: ✓ GROQ_API_KEY configured

---

## 🎯 What You Get

- ✅ **Medical Analysis** - Analyze eye, nose, tongue images
- ✅ **Report Generation** - Professional medical reports
- ✅ **Diet Plans** - Personalized nutrition plans
- ✅ **Doctor Finder** - Find hospitals & specialists
- ✅ **Appointments** - Schedule consultations

**All completely FREE!**

---

## 📊 Groq Models Available

```
- mixtral-8x7b-32768  (Recommended, balanced)
- llama2-70b-4096     (Powerful reasoning)
- gemma-7b-it         (Fast & efficient)
```

---

## 🔄 Switching Between Providers

### Use Groq (Free, recommended)
```env
USE_GROQ=true
GROQ_API_KEY=gsk_your_key
```

### Use Claude (Paid, best quality)
```env
USE_GROQ=false
ANTHROPIC_API_KEY=sk-ant-your_key
```

---

## ❓ Troubleshooting

### "GROQ_API_KEY not configured"
```bash
1. Go to: https://console.groq.com/keys
2. Create API key
3. Add to .env: GROQ_API_KEY=gsk_...
4. Restart server
```

### "Rate limit exceeded"
Groq has generous limits (~10 requests/minute free tier). Wait a moment and retry.

### "Connection timeout"
Check internet connection and try again.

---

## 💡 Tips

- Keep your API key private
- Don't commit `.env` to git
- Free tier is sufficient for testing
- Upgrade to paid tier if needed later

---

## 🎉 You're All Set!

Your system is now powered by **Groq** - completely free AI! 

Start the server:
```bash
python run_server.py
```

Open in browser:
```
http://127.0.0.1:8000
```

Upload medical images and start analyzing! 🏥

---

**Questions?** Check: https://console.groq.com
