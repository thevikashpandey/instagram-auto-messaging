import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from playwright.sync_api import sync_playwright

# ✅ JSON File Load from Railway Environment Variables
json_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
if not json_creds:
    raise ValueError("❌ Google Service Account JSON not found in Environment Variables!")

service_account_info = json.loads(json_creds)

# ✅ Google Sheets API Setup
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
client = gspread.authorize(creds)

# ✅ Google Sheet ID & Access
SHEET_ID = "11YkWvsAkEvB6FqFKIub_tcFZnpAMUMoInuvBGDvH89k"
sheet = client.open_by_key(SHEET_ID).sheet1

def fetch_google_sheet_message():
    today_date = datetime.today().strftime("%d-%m-%Y")
    current_hour = int(datetime.now().strftime("%H"))
    
    print(f"🔍 Searching data for Date: {today_date}")
    data = sheet.get_all_records()
    today_data = next((row for row in data if row['Date'] == today_date), None)
    
    if not today_data:
        print("❌ No data found for today’s date!")
        return None
    
    if 7 <= current_hour < 12:
        message = today_data['Morning Reply']
    elif 12 <= current_hour < 17:
        message = today_data['Afternoon Reply']
    elif 17 <= current_hour < 21:
        message = today_data['Evening Reply']
    else:
        message = today_data['Evening Reply 2']
    
    print(f"✅ Message Fetched: {message}")
    return message

def login_and_send_message():
    message = fetch_google_sheet_message()
    if not message:
        print("🚫 No message to send at this time.")
        return
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context()
        page = context.new_page()

        print("🔄 Opening Instagram Login Page...")
        page.goto("https://www.instagram.com/accounts/login/", timeout=30000)
        page.wait_for_selector("input[name='username']", timeout=15000)
        page.wait_for_selector("input[name='password']", timeout=15000)

        # ✅ Instagram Credentials (Replace with Environment Variables)
        insta_username = os.getenv("INSTA_USERNAME")
        insta_password = os.getenv("INSTA_PASSWORD")
        if not insta_username or not insta_password:
            raise ValueError("❌ Instagram Credentials Missing in Environment Variables!")

        page.locator("input[name='username']").fill(insta_username)
        page.locator("input[name='password']").fill(insta_password)
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(5000)

        # ✅ Handle Popups
        for _ in range(2):  
            try:
                page.wait_for_selector("text=Not Now", timeout=5000)
                page.locator("text=Not Now").click()
            except:
                pass  

        print("📩 Redirecting to Instagram Chat...")
        page.goto("https://www.instagram.com/direct/t/17847260585702538/", timeout=20000)
        page.wait_for_timeout(5000)

        try:
            message_box = page.locator("div[role='textbox']")
            message_box.click()
            message_box.fill("")
            message_box.type(message, delay=50)
            page.keyboard.press("Enter")
            print("✅ Message Sent!")
        except:
            print("❌ Message Box Not Found! Maybe Instagram updated UI.")

        browser.close()
        print("🚪 Browser Closed Successfully!")

# ✅ Execute Script
login_and_send_message()
