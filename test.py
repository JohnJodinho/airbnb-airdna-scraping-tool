import json
from playwright.sync_api import sync_playwright

def save_cookies_to_json(url, output_file):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to the initial URL
        page.goto(url, timeout=90000)
        
        # Wait for URL to change (modify timeout as needed)
        page.wait_for_function("window.location.href !== arguments[0]", arg=url, timeout=60000)
        
        # Get cookies
        cookies = context.cookies()
        
        # Save cookies to JSON file
        with open(output_file, "w") as f:
            json.dump(cookies, f, indent=4)
        
        print(f"Cookies saved to {output_file}")
        
        browser.close()

save_cookies_to_json("https://app.airdna.co/data/us", "session_cookies.json")
