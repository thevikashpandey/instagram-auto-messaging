import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from playwright.sync_api import sync_playwright

# ✅ Google Sheets API ka Scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ✅ JSON Key File ka path
KEY_FILE = "insta-bot-project-455515-2867fd12481e.json"

# ✅ Google Sheet ID
SHEET_ID = "11YkWvsAkEvB6FqFKIub_tcFZnpAMUMoInuvBGDvH89k"  # Google Sheet ka ID

# ✅ Credentials Load karo
creds = Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# ✅ Open Google Sheet
sheet = client.open_by_key(SHEET_ID).sheet1  # First sheet select

# ✅ Aaj ka message fetch karne ka function
def fetch_google_sheet_message():
    today_date = datetime.today().strftime("%d-%m-%Y")  # Format: DD-MM-YYYY
    current_hour = int(datetime.now().strftime("%H"))  # Current Hour

    print(f"🔍 Searching data for Date: {today_date}")

    # ✅ Google Sheet ka pura data read karo
    data = sheet.get_all_records()

    # ✅ Aaj ki Date ka data find karo
    today_data = next((row for row in data if row['Date'] == today_date), None)

    if not today_data:
        print("❌ No data found for today’s date!")
        return None

    # ✅ Time Slot Ke Hisab Se Message Pick Karo
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

        # ✅ Handle "Save Your Login Info?" popup
        try:
            page.wait_for_selector("text=Not Now", timeout=5000)
            page.locator("text=Not Now").click()
            print("⚠️ Clicked 'Not Now' on Save Login Info popup")
            page.wait_for_timeout(5000)
        except:
            print("✅ No 'Save Login Info' popup detected.")

        # ✅ Handle "Turn on Notifications?" popup on Login
        try:
            page.wait_for_selector("text=Not Now", timeout=5000)
            page.locator("text=Not Now").click()
            print("⚠️ Clicked 'Not Now' on Turn on Notifications popup")
            page.wait_for_timeout(5000)
        except:
            print("✅ No 'Turn on Notifications' popup detected.")

        # ✅ Redirect to Instagram Chat
        print("📩 Redirecting to Instagram Chat...")
        page.goto("https://www.instagram.com/direct/t/17847260585702538/", timeout=20000)
        page.wait_for_timeout(5000)

        # ✅ Handle "Turn on Notifications?" popup on Chat Page
        try:
            page.wait_for_selector("text=Not Now", timeout=5000)
            page.locator("text=Not Now").click()
            print("⚠️ Clicked 'Not Now' on Chat Page Notifications popup")
            page.wait_for_timeout(5000)
        except:
            print("✅ No 'Turn on Notifications' popup detected on Chat Page.")

        # ✅ Wait for Message Input Box Properly with Correct Selector
        print("⌛ Waiting for Message Input Box...")
        for attempt in range(3):  # Try 3 times with delay
            try:
                message_box = page.locator("div[role='textbox']")
                if message_box.is_visible():
                    print("✅ Message Box Found!")
                    break
            except:
                print(f"🔄 Attempt {attempt + 1}: Message Box not found, retrying...")
                page.wait_for_timeout(2000)  # Wait 2 sec before retrying

        # ✅ Send Message with Proper Typing
        try:
            message_box.click()
            page.wait_for_timeout(1000)  # Small wait before typing
            message_box.fill("")  # Clear any placeholder text
            message_box.type(message, delay=50)
            page.keyboard.press("Enter")
            print("✅ Message Sent!")

            # ✅ 5-second delay before closing browser
            print("⏳ Waiting 5 seconds before closing the browser...")
            page.wait_for_timeout(5000)
        except:
            print("❌ Message Box Not Found! Maybe Instagram updated UI.")

        browser.close()
        print("🚪 Browser Closed Successfully!")

# Run the function
login_and_send_message()
# ==========================================================================================