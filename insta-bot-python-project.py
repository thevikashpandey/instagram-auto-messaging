import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from playwright.sync_api import sync_playwright

def load_google_credentials():
    json_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not json_creds:
        raise ValueError("❌ Google Service Account JSON not found in Environment Variables!")
    try:
        return json.loads(json_creds)
    except json.JSONDecodeError:
        raise ValueError("❌ Invalid JSON Format in Environment Variable!")

def fetch_google_sheet_message():
    creds = Credentials.from_service_account_info(load_google_credentials(), scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    sheet = client.open_by_key("11YkWvsAkEvB6FqFKIub_tcFZnpAMUMoInuvBGDvH89k").sheet1
    
    today_date = datetime.today().strftime("%d-%m-%Y")
    current_hour = int(datetime.now().strftime("%H"))
    data = sheet.get_all_records()
    today_data = next((row for row in data if row['Date'] == today_date), None)
    
    if not today_data:
        return None
    
    if 7 <= current_hour < 12:
        return today_data.get('Morning Reply', '')
    elif 12 <= current_hour < 17:
        return today_data.get('Afternoon Reply', '')
    elif 17 <= current_hour < 21:
        return today_data.get('Evening Reply', '')
    else:
        return today_data.get('Evening Reply 2', '')

def login_and_send_message():
    message = fetch_google_sheet_message()
    if not message:
        print("🚫 No message to send at this time.")
        return
    
    insta_username = os.getenv("INSTA_USERNAME")
    insta_password = os.getenv("INSTA_PASSWORD")
    if not insta_username or not insta_password:
        raise ValueError("❌ Instagram Credentials Missing in Environment Variables!")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=1000)  # ✅ Headless Mode for Railway
        context = browser.new_context()
        page = context.new_page()
        
        print("🔄 Opening Instagram Login Page...")
        page.goto("https://www.instagram.com/accounts/login/", timeout=60000)
        page.wait_for_selector("input[name='username']", timeout=20000).fill(insta_username)
        page.wait_for_selector("input[name='password']", timeout=20000).fill(insta_password)
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(8000)
        
        print("📩 Redirecting to Instagram Chat...")
        page.goto("https://www.instagram.com/direct/t/17847260585702538/", timeout=60000)
        page.wait_for_timeout(5000)
        
        try:
            message_box = page.locator("div[role='textbox']")
            message_box.click()
            message_box.fill(message)
            page.keyboard.press("Enter")
            print("✅ Message Sent!")
        except:
            print("❌ Message Box Not Found! Maybe Instagram updated UI.")
        
        browser.close()
        print("🚪 Browser Closed Successfully!")

if __name__ == "__main__":
    login_and_send_message()
