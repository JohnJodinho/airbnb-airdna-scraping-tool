import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
def extract_script_json(url):
    max_retries = 5
    base_backoff = 1  # in seconds
    data = {}
    success = "failure"
    final_url = url
    
    for attempt in range(1, max_retries + 1):
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()

                # Open the given URL
                page.goto(url, wait_until="domcontentloaded")

                try:
                    # Wait for the page to load completely and the specific <div> to appear
                    page.wait_for_selector("div._1a6d9c4", timeout=15000)

                    # Get the content of the script tag with id="data-deferred-state-0"
                    script_content = page.locator("script#data-deferred-state-0").inner_text()
                except Exception as e:
                    print(f"Error in extract script JSON: {e}")
                    

                # Parse the script content as JSON
                try:
                    data = json.loads(script_content)
                except json.JSONDecodeError as e:
                    print("Failed to parse JSON from script tag:", e)
                    data = {}

                

                print(f"JSON data extracted ")

                # Close browser
                browser.close()
                success = "success"
                final_url = page.url
                break  
        except PlaywrightTimeoutError as e:
            print(f"Attempt {attempt}: Timeout while waiting for the element. Error: {e}")
        except Exception as e:
            print(f"Attempt {attempt}: An error occurred. Error: {e}")

        if attempt < max_retries:
            backoff_time = base_backoff * (2 ** (attempt - 1))
            print(f"Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)
        else:
            print("Max retries reached. Exiting...")

    return success, final_url, data
    
   






















