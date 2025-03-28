import json
from playwright.sync_api import sync_playwright

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
                browser.close()
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


vrbo_urls = [
    "https://www.vrbo.com/4718097ha",
    "https://www.vrbo.com/1501155",
    "https://www.vrbo.com/1696156",
    "https://www.vrbo.com/3563604",
    "https://www.vrbo.com/1632887",
]                    
    

for url in vrbo_urls:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        data = extract_apollo_state(page)
        print(extract_hostname(data))
        browser.close()



# my_json = "apollo_state.json"

# with open(my_json, "r") as f:
#     data = json.load(f)

# print(extract_hostname(data))