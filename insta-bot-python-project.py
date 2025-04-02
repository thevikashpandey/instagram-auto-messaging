import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from playwright.sync_api import sync_playwright
import json
import os

# ✅ Environment Variable se JSON Path Fetch Karo
json_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
if not json_path or not os.path.exists(json_path):
    raise FileNotFoundError(f"\n❌ Error: JSON file not found at {json_path}\n")

# ✅ JSON File Load Karo
with open(json_path, "r") as file:
    service_account_info = json.load(file)

# ✅ Google Sheets API Credentials Load Karo
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
client = gspread.authorize(creds)

# ✅ Google Sheet ID
SHEET_ID = "11YkWvsAkEvB6FqFKIub_tcFZnpAMUMoInuvBGDvH89k"
sheet = client.open_by_key(SHEET_ID).sheet1  # First sheet select

def fetch_google_sheet_message():
    today_date = datetime.today().strftime("%d-%m-%Y")  # Format: DD-MM-YYYY
    current_hour = int(datetime.now().strftime("%H"))  # Current Hour
    
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

        page.locator("input[name='username']").fill("vikash.panday002@gmail.com")
        page.locator("input[name='password']").fill("vikash@8744")
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(5000)

        try:
            page.wait_for_selector("text=Not Now", timeout=5000)
            page.locator("text=Not Now").click()
        except:
            print("✅ No 'Save Login Info' popup detected.")

        try:
            page.wait_for_selector("text=Not Now", timeout=5000)
            page.locator("text=Not Now").click()
        except:
            print("✅ No 'Turn on Notifications' popup detected.")
        
        print("📩 Redirecting to Instagram Chat...")
        page.goto("https://www.instagram.com/direct/t/17847260585702538/", timeout=20000)
        page.wait_for_timeout(5000)

        try:
            page.wait_for_selector("text=Not Now", timeout=5000)
            page.locator("text=Not Now").click()
        except:
            print("✅ No 'Turn on Notifications' popup detected on Chat Page.")
        
        message_box = page.locator("div[role='textbox']")
        if message_box.is_visible():
            message_box.click()
            message_box.fill("")
            message_box.type(message, delay=50)
            page.keyboard.press("Enter")
            print("✅ Message Sent!")
        else:
            print("❌ Message Box Not Found! Maybe Instagram updated UI.")
        
        browser.close()
        print("🚪 Browser Closed Successfully!")

login_and_send_message()