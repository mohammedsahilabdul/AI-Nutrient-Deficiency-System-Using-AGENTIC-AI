# 🚀 Quick Start Guide - Streamlit Version

## 5-Minute Setup

### Step 1: Get API Keys (5 min)

#### Option A: GROQ (Recommended - FREE)
1. Visit: https://console.groq.com/keys
2. Sign up (free)
3. Generate API key
4. Copy key

#### Option B: Anthropic Claude
1. Visit: https://console.anthropic.com
2. Create account
3. Add payment method
4. Generate API key

#### Gmail for Email Confirmations
1. Open: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Generate 16-character password
4. Copy password

### Step 2: Configure .env File (2 min)

Create file named `.env` in project root with:

```env
# LLM (use GROQ for free)
USE_GROQ=true
GROQ_API_KEY=gsk_YOUR_KEY_HERE

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# Hospital Search
SERPER_API_KEY=your_serper_key_here

# Debug
DEBUG_MODE=true
```

### Step 3: Install & Run (2 min)

```bash
# Windows
run_streamlit.bat

# Linux/Mac
bash run_streamlit.sh
```

**That's it!** The app opens at http://localhost:8501

## Using the App

### Upload & Analyze (Step 1)
1. Enter patient info
2. Upload 3 images: eye, nails, tongue
3. Click "Analyze Images"
4. Wait 1-2 minutes for results

### View Results (Step 2)
- See diagnosis
- Read medical report
- Get diet plan
- View doctor recommendations

### Book Appointment (Step 3)
1. Select doctor & hospital
2. Choose date & time
3. Submit booking
4. Get confirmation email

## Troubleshooting

### "API Key Error"
→ Check .env file format, ensure key is correct

### "Email not sent"
→ Verify email credentials in .env
→ Use Gmail App Password (not regular password)

### "Images not analyzing"
→ Ensure images are JPG/PNG
→ Check file size < 10MB
→ Clear browser cache and refresh

### "Module not found"
→ Run: `pip install -r requirements.txt`
→ Check venv is activated

## Free Tier Limits

- **GROQ**: Generous free tier for testing
- **Serper**: 100 free searches/month
- **Gmail**: Unlimited for personal use

## Next Steps

1. ✅ Get API keys
2. ✅ Create .env file
3. ✅ Run run_streamlit.bat
4. ✅ Upload test images
5. ✅ Book appointment
6. ✅ Check email confirmation

## Get Help

- Check STREAMLIT_README.md for full documentation
- Review app logs in terminal
- Verify all API keys are active

---

**Ready?** Run `run_streamlit.bat` now! 🚀
