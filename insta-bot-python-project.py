import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from playwright.sync_api import sync_playwright
import json
import os

# ✅ JSON File ka Automatic Path
json_path = os.path.join(os.getcwd(), "insta-bot-project-455515-2867fd12481e.json")

# ✅ Check if JSON File Exists
if not os.path.exists(json_path):
    print(f"❌ Error: JSON file not found at {json_path}")
    exit(1)

# ✅ Google Sheets API ka Scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ✅ Load Credentials from JSON File
with open(json_path, "r") as file:
    service_account_info = json.load(file)

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
        message = today_data['Morning Reply']
    elif 12 <= current_hour < 17:
        message = today_data['Afternoon Reply']
    elif 17 <= current_hour < 21:
        message = today_data['Evening Reply']
    else:
        message = today_data['Evening Reply 2']

    print(f"✅ Message Fetched: {message}")
    return message

# ✅ Instagram Login & Message Send Function
def login_and_send_message():
    message = fetch_google_sheet_message()
    if not message:
        print("🚫 No message to send at this time.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False, slow_mo=100)
        context = browser.new_context()
        page = context.new_page()

        print("🔄 Opening Instagram Login Page...")
        page.goto("https://www.instagram.com/accounts/login/", timeout=30000)
        page.wait_for_selector("input[name='username']", timeout=15000)
        page.wait_for_selector("input[name='password']", timeout=15000)

        page.locator("input[name='username']").fill("vikash.panday002@gmail.com")
        page.locator("input[name='password']").fill("vikash@8744")
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
        for attempt in range(3):
            try:
                message_box = page.locator("div[role='textbox']")
                if message_box.is_visible():
                    print("✅ Message Box Found!")
                    break
            except:
                print(f"🔄 Attempt {attempt + 1}: Message Box not found, retrying...")
                page.wait_for_timeout(2000)

        try:
            message_box.click()
            page.wait_for_timeout(1000)
            message_box.fill("")
            message_box.type(message, delay=50)
            page.keyboard.press("Enter")
            print("✅ Message Sent!")
            print("⏳ Waiting 5 seconds before closing the browser...")
            page.wait_for_timeout(5000)
        except:
            print("❌ Message Box Not Found! Maybe Instagram updated UI.")

        browser.close()
        print("🚪 Browser Closed Successfully!")

# ✅ Run the Function
login_and_send_message()
