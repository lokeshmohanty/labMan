#!/usr/bin/env python3
"""
Lab Manager Email Configuration Test Script

This script tests your email configuration to ensure notifications will work.
Run this after configuring SMTP_PASSWORD in .env
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration from labman.lib.users
try:
    from labman.lib.users import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL
    
    # Get Lab Name
    LAB_NAME = os.getenv('LAB_NAME', 'Lab Manager')
    
    print("✓ Loaded configuration")
    print(f"  SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"  Username: {SMTP_USERNAME}")
    print(f"  Sender: {SENDER_EMAIL}")
    print(f"  Lab Name: {LAB_NAME}")
    print()
except ImportError as e:
    print(f"✗ Error importing configuration: {e}")
    print("Ensure labman package is installed or PYTHONPATH is set.")
    sys.exit(1)

def test_email():
    """Test email sending capability"""
    
    # Check if password is configured
    if not SMTP_PASSWORD or SMTP_PASSWORD == 'your-smtp-password':
        print("✗ Error: SMTP_PASSWORD not configured!")
        print()
        print("Please update .env with your Gmail App Password:")
        print(f"1. Go to https://myaccount.google.com (sign in as {SMTP_USERNAME or 'your email'})")
        print("2. Security → 2-Step Verification (enable if needed)")
        print("3. Security → App passwords → Generate for 'Mail'")
        print("4. Copy the 16-character password")
        print("5. Update SMTP_PASSWORD in .env")
        print()
        return False
    
    print("Testing email configuration...")
    print()
    
    try:
        # Create test message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'{LAB_NAME} - Email Test'
        msg['From'] = SENDER_EMAIL
        msg['To'] = SMTP_USERNAME  # Send to self for testing
        
        # Plain text version
        text = f"""
Hello,

This is a test email from the {LAB_NAME} Management System.

If you received this email, your SMTP configuration is working correctly!

The system is now ready to send:
- User activation emails
- Meeting notifications
- Password reset emails
- Content upload notifications

Best regards,
{LAB_NAME} System
"""
        
        # HTML version
        html = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #3E2723;">
    <h2 style="color: #8B4513;">Email Test Successful! ✓</h2>
    <p>This is a test email from the {LAB_NAME} Management System.</p>
    <p>If you received this email, your SMTP configuration is working correctly!</p>
    
    <div style="background-color: #FFF8DC; padding: 15px; border-radius: 4px; margin: 20px 0;">
        <h3 style="color: #8B4513;">The system is now ready to send:</h3>
        <ul>
            <li>User activation emails</li>
            <li>Meeting notifications</li>
            <li>Password reset emails</li>
            <li>Content upload notifications</li>
        </ul>
    </div>
    
    <p style="color: #6D4C41; font-size: 12px; margin-top: 30px;">
        Best regards,<br>
        {LAB_NAME} System<br>
    </p>
</body>
</html>
"""
        
        # Attach both versions
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            print("✓ Connected")
            
            print("Starting TLS encryption...")
            server.starttls()
            print("✓ TLS enabled")
            
            print(f"Authenticating as {SMTP_USERNAME}...")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            print("✓ Authentication successful")
            
            print(f"Sending test email to {SMTP_USERNAME}...")
            server.send_message(msg)
            print("✓ Email sent successfully!")
        
        print()
        print("=" * 60)
        print("SUCCESS! Email configuration is working correctly.")
        print("=" * 60)
        print()
        print(f"Check the inbox of {SMTP_USERNAME}")
        print(f"You should see an email with subject: '{LAB_NAME} - Email Test'")
        print()
        print("Next steps:")
        print("1. Run the application: python app.py")
        print("2. Login and change the admin password")
        print("3. Start adding users (they'll receive activation emails)")
        print()
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("✗ Authentication failed!")
        print()
        print("Common causes:")
        print("1. Incorrect App Password - generate a new one")
        print("2. 2-Step Verification not enabled on Gmail account")
        print("3. Using regular Gmail password instead of App Password")
        print()
        print("Solution:")
        print("1. Go to https://myaccount.google.com")
        print("2. Enable 2-Step Verification if not already enabled")
        print("3. Generate a new App Password (Security → App passwords)")
        print("4. Update SMTP_PASSWORD in .env")
        print()
        return False
        
    except smtplib.SMTPConnectError:
        print("✗ Connection failed!")
        print()
        print("Check:")
        print("1. Internet connection is working")
        print("2. Firewall allows outbound connections on port 587")
        print("3. SMTP_SERVER and SMTP_PORT are correct")
        print()
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
        print("Please check:")
        print("1. All settings in .env are correct")
        print("2. Internet connection is stable")
        print(f"3. Gmail account ({SMTP_USERNAME}) is accessible")
        print()
        return False

if __name__ == '__main__':
    print()
    print("=" * 60)
    print(f"{os.getenv('LAB_NAME', 'Lab Manager')} - Email Configuration Test")
    print("=" * 60)
    print()
    
    success = test_email()
    
    sys.exit(0 if success else 1)
