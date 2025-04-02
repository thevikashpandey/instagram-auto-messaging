import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from playwright.sync_api import sync_playwright
import json
import os

# ✅ Google Sheets API ka Scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ✅ JSON File se Credentials Load Karo
json_path = "insta-bot-project-455515-2867fd12481e.json"
if not os.path.exists(json_path):
    print(f"❌ Error: JSON file not found at {json_path}")
    exit(1)

with open(json_path, "r") as file:
    service_account_info = json.load(file)

# ✅ Credentials Load Karo
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
client = gspread.authorize(creds)

# ✅ Google Sheet ID
SHEET_ID = "11YkWvsAkEvB6FqFKIub_tcFZnpAMUMoInuvBGDvH89k"
sheet = client.open_by_key(SHEET_ID).sheet1  # First sheet select

# ✅ Aaj ka message fetch karne ka function
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
        message = today_data.get('Morning Reply', '')
    elif 12 <= current_hour < 17:
        message = today_data.get('Afternoon Reply', '')
    elif 17 <= current_hour < 21:
        message = today_data.get('Evening Reply', '')
    else:
        message = today_data.get('Evening Reply 2', '')

    if not message:
        print("❌ No valid message found!")
        return None

    print(f"✅ Message Fetched: {message}")
    return message

# ✅ Instagram Login & Message Send Function
def login_and_send_message():
    message = fetch_google_sheet_message()
    if not message:
        print("🚫 No message to send at this time.")
        return

    IG_USERNAME = os.getenv("IG_USERNAME", "vikash.panday002@gmail.com")
    IG_PASSWORD = os.getenv("IG_PASSWORD", "vikash@8744")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False, slow_mo=100)
        context = browser.new_context()
        page = context.new_page()

        print("🔄 Opening Instagram Login Page...")
        page.goto("https://www.instagram.com/accounts/login/", timeout=30000)
        page.wait_for_selector("input[name='username']", timeout=15000)
        page.wait_for_selector("input[name='password']", timeout=15000)

        page.locator("input[name='username']").fill(IG_USERNAME)
        page.locator("input[name='password']").fill(IG_PASSWORD)
        page.locator("button[type='submit']").click()

        print("⏳ Waiting for login to complete...")
        page.wait_for_timeout(5000)

        try:
            page.wait_for_selector("text=Not Now", timeout=5000)
            page.locator("text=Not Now").click()
            print("⚠️ Clicked 'Not Now' on Save Login Info popup")
            page.wait_for_timeout(5000)
        except:
            print("✅ No 'Save Login Info' popup detected.")

        try:
            page.wait_for_selector("text=Not Now", timeout=5000)
            page.locator("text=Not Now").click()
            print("⚠️ Clicked 'Not Now' on Turn on Notifications popup")
            page.wait_for_timeout(5000)
        except:
            print("✅ No 'Turn on Notifications' popup detected.")

        print("📩 Redirecting to Instagram Chat...")
        page.goto("https://www.instagram.com/direct/t/17847260585702538/", timeout=20000)
        page.wait_for_timeout(5000)

        try:
            page.wait_for_selector("text=Not Now", timeout=5000)
            page.locator("text=Not Now").click()
            print("⚠️ Clicked 'Not Now' on Chat Page Notifications popup")
            page.wait_for_timeout(5000)
        except:
            print("✅ No 'Turn on Notifications' popup detected on Chat Page.")

        print("⌛ Waiting for Message Input Box...")
        try:
            message_box = page.wait_for_selector("div[role='textbox']", timeout=10000)
            message_box.click()
            page.wait_for_timeout(1000)
            message_box.fill("")
            message_box.type(message, delay=50)
            page.keyboard.press("Enter")
            print("✅ Message Sent!")
            page.wait_for_timeout(5000)
        except Exception as e:
            print(f"❌ Error sending message: {e}")

        browser.close()
        print("🚪 Browser Closed Successfully!")

login_and_send_message()
