import asyncio
from pyppeteer import launch
import os
import shutil

# --- STREAM BOT AGENT - FINAL, CORRECTED REPLIT VERSION ---

# --- CONFIGURATION ---
# These must be set as Secrets in the Replit sidebar.
DISCORD_EMAIL = os.environ.get("DISCORD_EMAIL")
DISCORD_PASSWORD = os.environ.get("DISCORD_PASSWORD")
SERVER_NAME = os.environ.get("SERVER_NAME")
VOICE_CHANNEL_NAME = os.environ.get("VOICE_CHANNEL_NAME")

def get_stream_url():
    """Reads the URL from the control.txt file."""
    try:
        with open('control.txt', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    return line.strip()
    except FileNotFoundError:
        print("WARNING: control.txt not found. Using default URL.")
        return "https://www.replit.com/community"
    return "https://www.replit.com/community"

async def main( ):
    print("--- Starting STREAM Bot Agent ---")
    
    STREAM_URL = get_stream_url()
    if not all([DISCORD_EMAIL, DISCORD_PASSWORD, SERVER_NAME, VOICE_CHANNEL_NAME]):
        print("FATAL: One or more secrets (DISCORD_EMAIL, etc.) are not set. Stopping.")
        return

    # Automatically find the path to the Chromium executable.
    executable_path = shutil.which("chromium")
    if not executable_path:
        print("FATAL: Cannot find Chromium executable. Make sure 'pkgs.chromium' is in replit.nix.")
        return
    print(f"Found Chromium at: {executable_path}")

    browser = None
    page = None
    try:
        print("Launching browser...")
        browser = await launch(
            executablePath=executable_path,
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--start-maximized',
                '--window-size=1920,1080',
            ]
        )
        
        page = await browser.newPage()
        await page.setViewport({'width': 1920, 'height': 1080})

        # --- Login to Discord ---
        print("Navigating to Discord login...")
        await page.goto('https://discord.com/login', {'waitUntil': 'networkidle2'} )
        
        print("Entering credentials...")
        await page.type('input[name="email"]', DISCORD_EMAIL, {'delay': 100})
        await page.type('input[name="password"]', DISCORD_PASSWORD, {'delay': 100})
        await page.click('button[type="submit"]')
        
        print("Waiting for login to complete (with a longer timeout)...")
        # --- THIS IS THE FIX ---
        # Increased the timeout to 90 seconds to handle slow loading on Replit.
        await page.waitForNavigation({'waitUntil': 'networkidle2', 'timeout': 90000})
        # --- END OF FIX ---
        
        await page.waitForSelector("div[aria-label='Servers']", {'timeout': 90000})
        print("Login successful!")
        await asyncio.sleep(5)

        # --- Join Voice Channel ---
        print(f"Searching for server: '{SERVER_NAME}'...")
        server_selector = f"//div[@aria-label='Servers']//div[text()='{SERVER_NAME[0]}']"
        server_link = await page.waitForXPath(server_selector)
        await server_link.click()
        print("Server found.")
        await asyncio.sleep(3)

        print(f"Searching for voice channel: '{VOICE_CHANNEL_NAME}'...")
        channel_selector = f"//div[contains(@class, 'channelName')]//div[text()='{VOICE_CHANNEL_NAME}']"
        channel_link = await page.waitForXPath(channel_selector)
        await channel_link.click()
        print("Voice channel joined.")
        await asyncio.sleep(5)

        # --- Open Stream URL in New Tab ---
        print(f"Opening stream URL: {STREAM_URL}")
        stream_page = await browser.newPage()
        await stream_page.goto(STREAM_URL, {'waitUntil': 'networkidle2'})
        await stream_page.bringToFront()
        print("Stream page loaded.")
        await asyncio.sleep(5)

        # --- INITIATE SCREEN SHARE ---
        print("Attempting to start screen share...")
        screen_share_button = await page.waitForXPath("//button[@aria-label='Screen']")
        await screen_share_button.click()
        print("Screen share button clicked.")
        await asyncio.sleep(2)

        window_selector = "//div[text()='Chromium']" # The window name is now Chromium
        application_window = await page.waitForXPath(window_selector)
        await application_window.click()
        print("Application window selected.")
        await asyncio.sleep(2)

        go_live_button = await page.waitForXPath("//button[.//div[text()='Go Live']]")
        await go_live_button.click()
        print("Go Live button clicked. Stream should be active!")

        print("--- STREAM Bot Agent is LIVE. ---")
        await asyncio.Event().wait()

    except Exception as e:
        print(f"An error occurred: {e}")
        if page:
            await page.screenshot({'path': 'error.png'})
    finally:
        if browser:
            await browser.close()
        print("--- STREAM Bot Agent has shut down. ---")

if __name__ == "__main__":
    asyncio.run(main())
