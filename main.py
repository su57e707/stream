import asyncio
from pyppeteer import launch
import os
import time

# --- STREAM BOT AGENT - FINAL REPLIT VERSION ---

# --- CONFIGURATION ---
# These must be set as Secrets in the Replit sidebar.
DISCORD_EMAIL = os.environ.get("DISCORD_EMAIL")
DISCORD_PASSWORD = os.environ.get("DISCORD_PASSWORD")
SERVER_NAME = os.environ.get("SERVER_NAME")
VOICE_CHANNEL_NAME = os.environ.get("VOICE_CHANNEL_NAME")
STREAM_URL = os.environ.get("STREAM_URL", "https://www.youtube.com/" ) # Default URL if not set in secrets

async def main():
    print("--- Starting STREAM Bot Agent ---")
    
    if not all([DISCORD_EMAIL, DISCORD_PASSWORD, SERVER_NAME, VOICE_CHANNEL_NAME]):
        print("FATAL: One or more secrets (DISCORD_EMAIL, etc.) are not set. Stopping.")
        return

    browser = None
    try:
        print("Launching browser...")
        browser = await launch(
            executablePath='/nix/store/b2133331y5h68vj2g38g3f2k5v338q4v-google-chrome-stable-114.0.5735.198/bin/google-chrome-stable',
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
        
        print("Waiting for login to complete...")
        await page.waitForNavigation({'waitUntil': 'networkidle2'})
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

        window_selector = "//div[text()='Google Chrome']" 
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
    # The xvfb-run command is handled by the .replit file in this setup
    asyncio.run(main())
