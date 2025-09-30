import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime
import os

# ⚙️ CONFIGURATION - CHANGE THESE VALUES!
PRODUCT_URL = "https://www.extra.com/en-sa/mobiles-tablets/mobiles/smartphone/apple-iphone-17-pro-max-5g-6-9-inch-512gb-cosmic-orange/p/100462507"  # ← PUT YOUR PRODUCT URL HERE
CSS_SELECTOR = "d-flex out-of-stock-container svelte-1fmx4js"  # ← PUT YOUR BUTTON SELECTOR HERE

# Twilio Configuration (from environment variables)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'
YOUR_WHATSAPP_NUMBER = 'whatsapp:+966507869000'  # ← PUT YOUR NUMBER HERE

previous_state = None

def send_whatsapp_message(message):
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        msg = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message,
            to=YOUR_WHATSAPP_NUMBER
        )
        print(f"✅ WhatsApp sent: {msg.sid}")
        return True
    except Exception as e:
        print(f"❌ WhatsApp error: {e}")
        return False

def check_availability():
    global previous_state
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(PRODUCT_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        element = soup.select_one(CSS_SELECTOR)
        
        if not element:
            print(f"⚠️ Element not found: {CSS_SELECTOR}")
            return
        
        button_text = element.get_text(strip=True).lower()
        is_available = any(keyword in button_text for keyword in 
                          ['add to cart', 'buy now', 'add to bag', 'purchase', 'في السلة', 'اضف'])
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if is_available:
            print(f"[{current_time}] ✅ AVAILABLE - '{button_text}'")
            
            if previous_state == False or previous_state is None:
                message = f"🎉 Item is NOW AVAILABLE!\n\n" \
                         f"🔗 {PRODUCT_URL}\n" \
                         f"📦 Status: {button_text}\n" \
                         f"⏰ {current_time}\n\n" \
                         f"Hurry and grab it! 🏃"
                send_whatsapp_message(message)
        else:
            print(f"[{current_time}] ❌ UNAVAILABLE - '{button_text}'")
        
        previous_state = is_available
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("=" * 60)
    print("🔍 Product Monitor Started")
    print("=" * 60)
    print(f"URL: {PRODUCT_URL}")
    print(f"Checking every hour...")
    print("=" * 60)
    
    check_availability()
    schedule.every().hour.do(check_availability)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
