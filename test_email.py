#!/usr/bin/env python
"""
Test script to verify email configuration and send a test email
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_config():
    """Test if email credentials are properly configured"""
    
    print("="*60)
    print("🏥 AI MEDICAL SYSTEM - EMAIL CONFIG TEST")
    print("="*60)
    
    sender = os.getenv("GMAIL_SENDER", "").strip()
    password = os.getenv("GMAIL_PASSWORD", "").strip()
    
    print(f"\n📧 GMAIL_SENDER: {sender if sender else '❌ NOT SET'}")
    print(f"🔑 GMAIL_PASSWORD: {'✅ SET' if password else '❌ NOT SET'}")
    
    if not sender:
        print("\n❌ ERROR: GMAIL_SENDER is not set in .env file")
        print("   Solution: Add 'GMAIL_SENDER=your_email@gmail.com' to .env")
        return False
    
    if not password:
        print("\n❌ ERROR: GMAIL_PASSWORD is not set in .env file")
        print("   Solution: Add 'GMAIL_PASSWORD=your_app_password' to .env")
        return False
    
    print("\n✅ Credentials are configured!")
    return True


def test_smtp_connection():
    """Test SMTP connection to Gmail"""
    
    import smtplib
    
    sender = os.getenv("GMAIL_SENDER", "").strip()
    password = os.getenv("GMAIL_PASSWORD", "").strip()
    
    if not sender or not password:
        print("❌ Credentials not available - skipping SMTP test")
        return False
    
    print("\n" + "="*60)
    print("🔌 TESTING SMTP CONNECTION")
    print("="*60)
    
    try:
        print(f"\n🔄 Connecting to smtp.gmail.com:587...")
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.starttls()
            print("✅ TLS connection established")
            
            print(f"🔐 Logging in as {sender}...")
            server.login(sender, password.replace(" ", ""))
            print("✅ Login successful!")
            
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed!")
        print("   This usually means:")
        print("   1. Gmail password is incorrect")
        print("   2. 2-FA is not enabled")
        print("   3. App password wasn't generated correctly")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False


def test_send_email():
    """Test sending an actual email"""
    
    from features import EmailNotifier
    
    sender = os.getenv("GMAIL_SENDER", "").strip()
    
    if not sender:
        print("❌ No sender configured - skipping email test")
        return False
    
    print("\n" + "="*60)
    print("📧 TESTING EMAIL SEND")
    print("="*60)
    
    test_email = sender  # Send to self
    
    print(f"\n📤 Sending test email to {test_email}...")
    
    result = EmailNotifier.send_email(
        recipient=test_email,
        subject="🧪 AI Medical System - Test Email",
        body="""
This is a test email from the AI Medical Diagnostic System.

If you receive this email, your email configuration is working correctly!

You can now use the system to send medical reports to patients.

---
Best regards,
AI Medical Diagnostic System
""",
        html="""
<html>
    <body style="font-family: Arial, sans-serif;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; color: white; border-radius: 10px; margin-bottom: 20px;">
            <h2>🧪 AI Medical Diagnostic System - Test Email</h2>
        </div>
        <p>This is a test email from the AI Medical Diagnostic System.</p>
        <p><strong>If you receive this email, your email configuration is working correctly!</strong></p>
        <p>You can now use the system to send medical reports to patients.</p>
        <hr>
        <p><em>Best regards,<br>🏥 AI Medical Diagnostic System</em></p>
    </body>
</html>
"""
    )
    
    if result:
        print(f"✅ Email sent successfully!")
        return True
    else:
        print(f"❌ Email send failed - check server logs")
        return False


if __name__ == "__main__":
    
    # Run tests
    config_ok = test_email_config()
    
    if config_ok:
        smtp_ok = test_smtp_connection()
        
        if smtp_ok:
            send_ok = test_send_email()
            
            if send_ok:
                print("\n" + "="*60)
                print("✅ ALL TESTS PASSED!")
                print("="*60)
                print("\n📝 Your email system is fully configured and working.")
                print("   You can now send reports to patients!\n")
                sys.exit(0)
    
    print("\n" + "="*60)
    print("❌ TESTS FAILED")
    print("="*60)
    print("\n⚠️  Please check your email configuration in .env file\n")
    sys.exit(1)
