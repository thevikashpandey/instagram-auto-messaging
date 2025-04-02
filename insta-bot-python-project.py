import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from playwright.sync_api import sync_playwright

# ✅ JSON File Content ko Directly Paste Karo
service_account_info = {
  "type": "service_account",
  "project_id": "insta-bot-project-455515",
  "private_key_id": "2867fd12481e93540551c3c08cc6a679520b9420",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCyg8sMNTgCimlk\nIPwuYvYPmQpFUYqRmDFNKJLTGClWlmP/ChEz9PFjTOAJpxQJmW5a/xl47vIFcDdA\n5kY4Ki0ExBPQUrI8xxbCKwFFFd6WftR1ONIWg8dCHiBeGgsZQCJufO7e5zr4ZM/o\nBW6AyIHhTsci1iDdMQP1L8VaIo1YFuS/+a/B/Z4SJrApbgmroCqHUiZPCnurjLSW\nd7l28f2ky6+lUP4XjNBI3d/fJhpcLG51hzwCzrn5UO8BqanJ4gFsgO1sv87pkcp1\nl9x7/PiMU0LnPE3EWaXa2xNd+JsjherfQkpiFd92fYbeW0Cjjv2A092EoVABHXug\nBMMa9Z9rAgMBAAECggEACz/m8dQAvZg/YAH8Img2HXGFhizHULmIkdY2unrRUBWW\nI6JcxytuctWLYNBYoOo8XBurXUWhltolgT+BuVRfFefNX9l2RgI92uqe392q80z2\n0pRMGQMg8Xe4jnWRsXurL89LtlxYCQNBXtvIxPDdzncKcZWQ6J+IIlFqXG3E/oIH\n2mv1gSnCcOJkX2odI/ypN/4J8OGDavg5cGcL5uJaevf7ea+J6mrgR0EDKGEevUlF\n9xXhFwfUkui9Ake6AYNfs/2U8VCgqCLVe2M4UwIa0veG7KkukxMbIrDDGeiaETpe\n269P/4nXTH2i/1YqXXNiIKABMSYybXZXtI2VKqg5gQKBgQDgjJC9lsi12Fim8jCb\nw4JjG4K+FcLbOLfQYcXDN4YbA77ddVPqv2ZYy51SuHnL/8IVJNekKEJMddtBpqrH\nA527JGFGrECAKmoe2ib87Wuv0N0kBlyBRU7oGYXqgyaOfTwdqUpgPL39CfHIIu3G\np1XxJT9fgcnNDe/Y97wAyanA4QKBgQDLhJ9fsIVjiXdtJfpTnl2sWt9Hj/gkklen\nywq0y53ijBIAE8jI1yvg20Qe+oWuiYpBfZKyc3i9rUfQIM7Ect9pKC73RwhMGJHQ\nKjZAvGkBArkSWH/kh90bXaqWpsVn5xkTX/vmvvQJNNMvHQtvGX7evGSmmh/QFLoF\np5WjbxZNywKBgQDKIz+Yq8f6issjXhoL3i/d78H+Q7Cpj6FI4PsaBT2fy/theGEW\njT4g6QqykIZz8cRRLF1C1Ur5cY7yxootpT+0W8eFy0I1Hflx1IgMX93041xvNZrI\ndA/YOEGpHm7zDiGzwdXGVGfjBbS1qVvK3JAtCI7H9xomkUk8U6bWPrOlgQKBgAcA\nrjctrLlLDpfr2Zws884tZkdhFcm0W13Dp7+mzezwouHrzFnUxYa8JLDoL9dclixA\ntN59CKeGIdVwe4zY4wUMQ+lwQUHVCpdeDHXXxckqHdIax3PGlP4PEAKVBG/ZzMwU\n3mcHJQB4F9gkKLOO7gWd99yfqv6O6AOvy39PIDZXAoGAVZb2nMbHxl5APWRpCJhU\n1Ywk7WNaB3wZB62BpxxFN934AZUWpua+7600OG52mivowpm75eYYrdAWaPLTvpHb\nf4jDgZnjXYVS7R7L1Em893rJp2P36zh0O509vfIIz5tZAJeuKkWS/fv6VuPKSRji\n7oPZ+Z3eQyC1ayGvCKuioTs=\n-----END PRIVATE KEY-----\n",
  "client_email": "insta-bot-service@insta-bot-project-455515.iam.gserviceaccount.com",
  "client_id": "100516398673289923716",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/insta-bot-service%40insta-bot-project-455515.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# ✅ Google Sheets API Authentication
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
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
