import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from playwright.sync_api import sync_playwright
import json
import os
import gdown

# ✅ Google Drive JSON File ID (Agar Local File Na Mile to Drive se Lo)
DRIVE_FILE_ID = "1pOSTW0xlijy_TADy56LoOD0-m5dN6EaG"
LOCAL_JSON_PATH = r"C:\Users\Vikas\OneDrive\Desktop\insta-bot\instakeyfile.json"

# ✅ JSON File Check & Fetch
if os.path.exists(LOCAL_JSON_PATH):
    json_path = LOCAL_JSON_PATH
    print(f"✅ Using Local JSON File: {json_path}")
else:
    json_path = "service_account.json"
    drive_url = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"
    gdown.download(drive_url, json_path, quiet=False)
    print(f"✅ Downloaded JSON from Google Drive: {json_path}")

# ✅ JSON File Load Karo
if not os.path.exists(json_path):
    raise FileNotFoundError(f"\n❌ Error: JSON file not found at {json_path}\n")

with open(json_path, "r") as file:
    service_account_info = json.load(file)

# ✅ Google Sheets API Credentials
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
client = gspread.authorize(creds)

# ✅ Google Sheet ID
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

        # ✅ Instagram Credentials
        page.locator("input[name='username']").fill("vikash.panday002@gmail.com")
        page.locator("input[name='password']").fill("vikash@8744")
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
