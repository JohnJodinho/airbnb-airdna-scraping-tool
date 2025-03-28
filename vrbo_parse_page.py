from playwright.sync_api import sync_playwright, Page, expect
import re
import time
from bs4 import BeautifulSoup
import json
from get_address_google import fetch_address


def extract_apollo_state(page):
    # Extract all script tags
    scripts = page.query_selector_all("script")

    for script in scripts:
        content = script.inner_text()
        if "window.__APOLLO_STATE__" in content:
            # Extract JSON part
            try:
                json_str = content.split("window.__APOLLO_STATE__ = JSON.parse(", 1)[1].rsplit(");", 1)[0]
                parsed_json = json.loads(json.loads(json_str))  # Double JSON decode
              
                return parsed_json
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
    
    return None



def safe_get(d, keys, default=None):
    """Safely retrieves a nested value from a dictionary without KeyError or IndexError."""
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        elif isinstance(d, list) and isinstance(key, int) and 0 <= key < len(d):
            d = d[key]
        else:
            return default
    return d if d is not None else default

def extract_hostname(data):
    for key in data:
        if key.startswith("PropertyInfo"):
            property_info = data.get(key, {})
            
            for sub_key in property_info:
                if sub_key.startswith("propertyContentSectionGroups({\"searchCriteria\""):
                    about_property = property_info.get(sub_key, {}).get("aboutThisProperty", {}).get("sections", [])
                    about_host = property_info.get(sub_key, {}).get("aboutThisHost", {}).get("sections", [])

                    possible_values = [
                        safe_get(about_property, [0, "bodySubSections", 1, "elementsV2", 0, "elements", 0, "items", 1, "content", "primary", "value"]),
                        safe_get(about_host, [0, "bodySubSections", 0, "elementsV2", 0, "elements", 0, "header", "text"]),
                        safe_get(about_host, [0, "bodySubSections", 1, "expando", "expandButton", "text"])
                    ]

                    for item in possible_values:
                        if item and isinstance(item, str):
                            return item.replace("Hosted by", "").replace("View more about", "").strip()

    return None  # Return None only if all possible values are missing


def scrape_vrbo_data(url):
    max_retries = 5
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for attempt in range(1, max_retries + 1):
            try:
                # Navigate to the URL
                page.goto(url, timeout=90000)
                manager = None
                manager_json = extract_apollo_state(page)
                if manager_json:
                    manager = extract_hostname(manager_json)
                
                # Parse the page content with BeautifulSoup
                html_content = page.content()
                soup = BeautifulSoup(html_content, 'html.parser')
                

                # Extract latitude and longitude
                geo_meta = soup.find('div', itemprop='geo')
                latitude = geo_meta.find('meta', itemprop='latitude')['content'] if geo_meta else None
                longitude = geo_meta.find('meta', itemprop='longitude')['content'] if geo_meta else None

                # Get the address from the coordinates
                address = fetch_address(latitude, longitude) if latitude and longitude else None

                return {
                    
                    "url": url,
                    "address": address,
                    "manager": manager,
                    
                }

            except Exception as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt == max_retries:
                    print("Max retries reached. Exiting.")
                    return None
                else:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

        browser.close()


def process_vrbo_data(vrbo_dict):
    final_data = {}
    vrbo_id = vrbo_dict.get("vrbo_property_id")
    url = f"https://www.vrbo.com/{vrbo_id}"
    bedrooms = vrbo_dict.get("bedrooms")
    bathrooms = vrbo_dict.get("bathrooms")
    guests = vrbo_dict.get("accommodates")
    rating = vrbo_dict.get("rating")
    reviews = vrbo_dict.get("reviews")
    title = vrbo_dict.get("title")
    rev_potential = vrbo_dict.get("revenue_potential_ltm")
    market_name = vrbo_dict.get("market_name")
    latitude = vrbo_dict.get("location").get("lat")
    longitude = vrbo_dict.get("location").get("lng")
    the_license = None
    manager = None
    address = None

    result = scrape_vrbo_data(url)
    if result:
        address = result.get("address")
        manager = result.get("manager")
        url = result.get("url")
    if address is None:
        address = fetch_address(latitude, longitude)

    final_data["title"] = title
    final_data["airbnb_url"] = None
    final_data["bedrooms"] = bedrooms
    final_data["bathrooms"] = bathrooms
    final_data["guests"] = guests
    final_data["rating"] = rating
    final_data["reviews"] = reviews
    final_data["vrbo_url"] = url
    final_data["revenue potential"] = rev_potential
    final_data["market name"] = market_name
    # final_data["latitude"] = latitude
    # final_data["longitude"] = longitude
    final_data["license"] = the_license
    final_data["manager"] = manager
    final_data["address"] = address

    return final_data
        


# vrbo_urls = [
#     "https://www.vrbo.com/4718097ha",
#     "https://www.vrbo.com/1501155",
#     "https://www.vrbo.com/1696156",
#     "https://www.vrbo.com/3563604",
#     "https://www.vrbo.com/1632887",
# ]

# for url in vrbo_urls:
#     result = scrape_vrbo_data(url)
#     if result:
#         print(result)
#     else:
#         print(f"Failed to scrape data from {url}")

           
            

 


