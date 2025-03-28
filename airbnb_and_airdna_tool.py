from flask import (
    Flask, 
    jsonify, 
    request, 
    render_template, 
    send_from_directory, 
    g
)
import shutil
import webbrowser

from werkzeug.utils import secure_filename
import logging

import time
import json
import re
import sys

from playwright.sync_api import sync_playwright,TimeoutError as PlaywrightTimeoutError


import os 
from os import path


import sys
import threading



from datetime import datetime, timedelta

UPDATE_TRACKER_FILE = "market_update_tracker.json"

import random
from playwright.sync_api import TimeoutError

from all_paths import market_csv_dir, listings_json_dir, submarket_listings_dir, market_listings_dir, submarkets_csv_dir
from logger_util import custom_print, log_messages
from airbnb_process_json import process_airbnb_data
from confirm_entered_market import confirm_entered_market
from constants import BLOCK_RESOURCE_TYPES, BLOCK_RESOURCE_NAMES, initialize_user_info, set_user_details, get_user_details, set_google_maps_api_key, get_google_maps_api_key
from parse_numbers import parse_number_string
from get_listings import get_listings
from save_to_csv import save_json_to_csv, save_object_to_csv
from get_submarket import get_sub_markets
from vrbo_parse_page import process_vrbo_data
from get_path_name import resource_path



if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)




UPDATE_TRACKER_FILE = "market_update_tracker.json"
# Global credentials and variables
initialize_user_info()
AIRDNA_USERNAME, AIRDNA_PASSWORD = get_user_details()

current_final_json = None  # This will hold the path of the current JSON file being written
status = 0                 # Global status to track progress
stop_event = threading.Event()  # Event used to signal immediate stop of scraping
completed_json_file = None
completed_csv_file = None
# log_messages = [] 

logging.basicConfig(
    filename="app.log",  # Log file in the root directory
    level=logging.DEBUG,  # Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s"  # Log message format
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
app.logger.addHandler(console_handler)



# def custom_print(message):
#     """Log a message and make it available to the front-end."""
#     log_messages.append(f"{message}")
#     app.logger.info(message)  # For debugging and server-side logging



def login_and_save_session(page, login_url, email, password, storage_path):
    """
    Log in to the website and save the storage state with retry mechanism.

    Args:
        page: The Playwright page object to use for navigation and actions.
        login_url (str): The URL of the login page.
        email (str): The login email.
        password (str): The login password.
        storage_path (str): Path to save the storage state file.

    Returns:
        bool: True if login is successful, False otherwise.
    """
    max_retries = 5
    base_delay = 2  # Initial delay in seconds

    custom_print("Logging into AirDNA...")
    for attempt in range(max_retries):
        try:
            custom_print(f"Attempt {attempt + 1}: Navigating to the login page...")
            page.goto(login_url, timeout=120000)

            # Check if the email login button exists and click it if present
            if page.is_visible("a.email-btn"):
                custom_print("Clicking the email login button...")
                page.click("a.email-btn")
                page.wait_for_selector('input#login-email', timeout=15000)
            elif page.is_visible("input#login-email"):
                print("Login form is already visible.")
            else:
                raise Exception("Neither email login button nor login form is visible.")

            # Fill in the login form
            custom_print("Filling in the login credentials...")
            page.fill('input#login-email', email)
            page.fill('input#login-password', password)

            # Click the login button
            page.wait_for_selector('button[type="submit"]', timeout=15000)
            print("Clicking the login button...")
            page.click('button[type="submit"]')

            # Wait for the URL to change, indicating a successful login
            print("Waiting for URL to change after login...")
            page.wait_for_url(lambda url: url != login_url, timeout=15000)
            time.sleep(5)  # Additional wait time for session to be fully loaded

            # Save the storage state to a file
            print(f"Saving login session to {storage_path}...")
            page.context.storage_state(path=storage_path)
            custom_print("Login successful and session saved!")
            return True

        except PlaywrightTimeoutError as e:
            custom_print(f"Login attempt {attempt + 1} failed due to timeout: {e}")
        except Exception as e:
            custom_print(f"Login attempt {attempt + 1} failed due to error: {e}")

        if attempt < max_retries - 1:
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            custom_print(f"Retrying in {delay:.2f} seconds...")
            time.sleep(delay)

    print("All retry attempts failed. Unable to log in.")
    return False


def get_total_listings(user_query):
    final_number = None
    listing_id = None
   
    login_url = "https://app.airdna.co/data/login"
    
    
    storage_path = "state.json"
    # Confirm user input
    response = confirm_entered_market(user_query)

    if response[1]:
        user_pref = response[0]
        # custom_print(user_pref)
        details = response[1]
        statement = f"Scraping {user_pref}: {details['parent_market_name']}" if user_pref == "market" else f"Scraping {user_pref}: {details['name']}"
        custom_print(statement)
        
        # Get the total number of listings
        
        custom_print("Getting the total number of listings...")
        url = details["market_url"] if user_pref == "market" else details["submarket_url"]
        listing_id = f"market_id: {details['market_id']}" if user_pref == "market" else f"submarket_id: {details['id']}"
        custom_print(f"Market/Submarket ID: {listing_id}")
        def intercept_route(route):
            """intercept all requests and abort blocked ones"""
            if route.request.resource_type in BLOCK_RESOURCE_TYPES:
                # print(f'blocking background resource {route.request} blocked type "{route.request.resource_type}"')
                return route.abort()
            if any(key in route.request.url for key in BLOCK_RESOURCE_NAMES):
                # print(f"blocking background resource {route.request} blocked name {route.request.url}")
                return route.abort()
            return route.continue_()


        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # Use headless=True for production

            # Check if a saved session exists
            if os.path.exists(storage_path):
                print("Using saved session...")
                context = browser.new_context(storage_state=storage_path)
            else:
                print("No saved session found. Logging in...")
                context = browser.new_context()
                page = context.new_page()
                
                page.route("**/*", intercept_route)

                # Perform login and save session
                if not login_and_save_session(page, login_url, AIRDNA_USERNAME, AIRDNA_PASSWORD, storage_path):
                    print("Exiting: Failed to log in.")
                    
        
            # Create a page in the new context (with session)
            page = context.new_page()

            
            max_retries = 5

            for attempt in range(max_retries):
                try:
                    page.goto(url, timeout=120000, wait_until="commit")  
                    page.wait_for_load_state("domcontentloaded")  # Wait for essential DOM elements to be ready
                    # Wait indefinitely for the element to appear
                    button_selector = "button.MuiButtonBase-root.MuiTab-root.MuiTab-textColorPrimary"
                    page.wait_for_selector(button_selector, timeout=120000)  # Ensure button is available
  

                    buttons = page.query_selector_all(button_selector)

                    for btn in buttons:
                        text = btn.inner_text().strip()
                        if text.endswith("STR Listings") or text.endswith("STR Listing"):
                            button_text = text.rsplit(" STR Listing", 1)[0].rsplit(" STR Listings", 1)[0]
                            print("Extracted Text:", button_text)
                            final_number = parse_number_string(button_text.strip())
                            custom_print(f"Total number of listings: {final_number}")
                            break  # Stop once we find the first matching button


                    break  # Exit the loop if successful

                except TimeoutError as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt + random.uniform(0, 1)  # Exponential backoff with jitter
                        print(f"TimeoutError: {e}. Retrying in {wait_time:.2f} seconds...")
                        time.sleep(wait_time)
                    else:
                        print(f"TimeoutError: {e}. Max retries reached. Exiting...")
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt + random.uniform(0, 1)  # Exponential backoff with jitter
                        print(f"Error: {e}. Retrying in {wait_time:.2f} seconds...")
                        time.sleep(wait_time)
                    else:
                        print(f"Error: {e}. Max retries reached. Exiting...")

        
    else:
        custom_print("Invalid market or submarket. Please try again.")
    return final_number, listing_id


def get_listings_json(user_query):
    """
    Scrapes listings based on the user_query.
    If stop_event is set, it will abort scraping immediately and delete any partially saved JSON file.
    Returns the path to the final JSON file, or None if interrupted/failed.
    """
    global status, current_final_json
    status = 0

    # Get total listings and market identifier using your existing function
    total_listings_result = get_total_listings(user_query)
    total_listings = total_listings_result[0]
    market_type = "submarket" if "submarket" in total_listings_result[1] else "market"
    listing_id = total_listings_result[1].split(":")[1].strip() 

    listings_folder = listings_json_dir
    if not os.path.exists(listings_folder):
        os.makedirs(listings_folder)

    # If total_listings is found, begin scraping
    if total_listings:
        custom_print("Getting the listings...")
        # Choose proper parameter based on market type
        if market_type == "market":
            result = get_listings(total_listings, market_id=listing_id)
        else:
            result = get_listings(total_listings, submarket_id=listing_id)
        
        if result[0] == "Success":
            with open(result[1], "r", encoding="utf-8") as file:
                json_data = json.load(file)
            final_json = os.path.join(listings_folder, f"{listing_id}_listings.json")
            final_json = resource_path(final_json)
            current_final_json = final_json

            # Load existing listings if any, or start fresh
            if os.path.exists(final_json):
                with open(final_json, "r", encoding="utf-8") as file:
                    all_listings = json.load(file)
            else:
                all_listings = []

            processed_count = len(all_listings)
            total_listings_list = json_data["payload"]["listings"]

            # temp_total_listings = len([airbnb_data for airbnb_data in total_listings_list if airbnb_data.get("airbnb_property_id")])
            for index in range(processed_count, len(total_listings_list)):
                # Check if a stop signal has been received
                if stop_event.is_set():
                    custom_print("Scraping stopped by user.")
                    if os.path.exists(final_json):
                        os.remove(final_json)
                    current_final_json = None
                    return None

                # Process each listing
                listing = total_listings_list[index]
                if listing.get("airbnb_property_id"):
                    custom_print(f"Processing Airbnb data with id {listing['airbnb_property_id']}...")
                    airbnb_data = process_airbnb_data(listing)
                    all_listings.append(airbnb_data)
                    status = int(len(all_listings) / int(total_listings) * 100)
                    with open(final_json, "w", encoding="utf-8") as file:
                        json.dump(all_listings, file, indent=4)
                elif listing["vrbo_property_id"]:
                    custom_print(f"Processing VRBO data with id {listing['vrbo_property_id']}...")
                    vrbo_data = process_vrbo_data(listing)
                    all_listings.append(vrbo_data)
                    status = int(len(all_listings) / int(total_listings) * 100)
                    with open(final_json, "w", encoding="utf-8") as file:
                        json.dump(all_listings, file, indent=4)
              
           
          

            custom_print(f"Done extracting listings for {market_type} with id {listing_id}.")
            return final_json
    else:
        custom_print(f"Failed to get listings for {market_type} with id: {listing_id}.")
        return None

                
     


def get_markets_as_csv(destination_folder=market_csv_dir):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    with open("markets.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    csv_file_name = os.path.join(destination_folder, "markets.csv")
    csv_file_name = resource_path(csv_file_name)
    markets_list = []
    for market in data:
        market_dict = {}
        market_dict["id"] = market["market_id"]
        market_dict["name"] = market["parent_market_name"]
        market_dict["url"] = market["market_url"]
        market_dict["total submarkets"] = len(market["submarket"])
        markets_list.append(market_dict)
    
    save_object_to_csv(markets_list, csv_file_name)
    return csv_file_name

   
    

def get_submarkets_as_csv(market_id, destination_folder=submarkets_csv_dir):

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    with open("markets.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    submarkets_list = []
    return_statement = "failure"
    csv_file_name = None
    for market in data:
        if market["market_id"] == market_id:
            for submarket in market["submarket"]:
                submarket_dict = {}
                submarket_dict["id"] = submarket["id"]
                submarket_dict["name"] = submarket["name"]
                submarket_dict["url"] = submarket["submarket_url"]
                submarkets_list.append(submarket_dict)
            csv_file_name = os.path.join(destination_folder, f"submarkets_{market['parent_market_name'].replace(' ', '')}_{market_id.replace('-', '')}.csv")
            csv_file_name = resource_path(csv_file_name)
            return_statement = "success"
            break
    if return_statement == "success":
        save_object_to_csv(submarkets_list, csv_file_name)

    return return_statement, csv_file_name
    

def should_update_markets():
    """Check if the markets should be updated (once every week)."""
    # If the tracker file doesn't exist, we should update.
    if not os.path.exists(UPDATE_TRACKER_FILE):
        return True
    try:
        with open(UPDATE_TRACKER_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        last_update_str = data.get("last_update")
        if not last_update_str:
            return True

        last_update = datetime.fromisoformat(last_update_str)
        # Check if more than 7 days have passed.
        if datetime.now() - last_update > timedelta(weeks=1):
            return True
        return False
    except Exception as e:
        custom_print(f"Error reading update tracker: {e}")
        # In case of error, it's safer to update.
        return True

def update_market_tracker():
    """Update the tracker file with the current time."""
    try:
        with open(UPDATE_TRACKER_FILE, "w", encoding="utf-8") as file:
            json.dump({"last_update": datetime.now().isoformat()}, file, indent=4)
    except Exception as e:
        custom_print(f"Error updating market tracker: {e}")

def update_markets():
    """Update markets only if a week has passed since the last update."""
    if should_update_markets():
        try:
            custom_print("Updating markets and submarkets...")
            get_sub_markets("us")
            update_market_tracker()  # Record the update time.
            custom_print("Markets and submarkets updated.")
        except Exception as e:
            custom_print(f"Error updating markets and submarkets: {e}")
    else:
        custom_print("Market update not required yet; last update was less than a week ago.")

def clear_submarket_listings(folder = submarket_listings_dir):
    
    
    # Check if the folder exists before proceeding
    if not os.path.exists(folder):
        print(f"The folder '{folder}' does not exist.")
        return

    # Loop through all items in the folder
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        item_path = resource_path(item_path)
        try:
            # If item is a file or symbolic link, remove it
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
                print(f"Deleted file: {item_path}")
            # If item is a directory, remove it and its contents
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Deleted directory: {item_path}")
        except Exception as e:
            print(f"Failed to delete {item_path}. Reason: {e}")

@app.route('/')
def home():
    global status
    status = 0
    clear_submarket_listings(listings_json_dir)
    clear_submarket_listings(submarket_listings_dir)
    clear_submarket_listings(market_listings_dir)
    clear_submarket_listings(submarkets_csv_dir)
    

    try:
        log_messages.clear()
    except Exception as e:
        print(f"Error clearing log messages: {e}")

    # Run market update in a background thread.
    threading.Thread(target=update_markets).start()
    
    # Serve the home page immediately.
    return render_template("index.html")

@app.route('/start-scraping', methods=['POST'])
def start_scraping():
    """
    Starts the scraping process using the provided user_query.
    The process is run in a background thread. Progress is tracked in the global 'status' variable.
    When scraping is completed, save_json_to_csv is called to save the JSON to CSV.
    """
    global status, stop_event
    status = 0
    log_messages.clear()
    clear_submarket_listings(listings_json_dir)
    clear_submarket_listings(submarket_listings_dir)
    clear_submarket_listings(market_listings_dir)
    clear_submarket_listings(submarkets_csv_dir)

    data = request.get_json()
    if not data or 'user_query' not in data:
        return jsonify({"error": "Invalid request. 'user_query' is required."}), 400

    user_query = data['user_query']
    custom_print(f"Starting scraping for: {user_query}")

    # Ensure any previous stop signal is cleared
    stop_event.clear()

    def scraping_task():
        final_json = get_listings_json(user_query)
        if final_json is None:
            custom_print("Scraping was interrupted or failed.")
        else:
            custom_print("Scraping completed successfully.")
            # After successful scraping, convert JSON to CSV.
            try:
                
                # After successful scraping
                csv_file = final_json.replace(".json", ".csv")
                save_json_to_csv(final_json)
                # Update the global variables so they can be served later
                global completed_json_file, completed_csv_file
                completed_json_file = final_json
                completed_csv_file = csv_file
                custom_print(f"JSON data saved to CSV: {csv_file}")

                
            except Exception as e:
                custom_print(f"Error saving CSV: {e}")

    # Start the scraping task in a background thread
    threading.Thread(target=scraping_task).start()
    return jsonify({"success": True}), 200

@app.route('/stop-scraping', methods=['POST'])
def stop_scraping():
    """
    Immediately stops the scraping process by setting the stop_event.
    Also deletes the current JSON file if it exists.
    """
    global status, current_final_json
    status = 0
    stop_event.set()
    if current_final_json and os.path.exists(current_final_json):
        try:
            os.remove(current_final_json)
            custom_print("Current JSON file deleted.")
        except Exception as e:
            custom_print(f"Error deleting JSON file: {e}")
        current_final_json = None
    custom_print("Scraping stopped by user.")
    return jsonify({"message": "Scraping stopped and file deleted."}), 200

@app.route('/get-logs', methods=['GET'])
def get_logs():
    """Provide the current log messages to the front-end."""
    
    return jsonify(log_messages)


@app.route('/check_status', methods=['GET'])
def check_status():
    """
    API endpoint to check the status of the scraping process.
    """
    # print(f"Current status: {status}")
    return jsonify({"status": status}), 200



# Route to configure AirDNA logins
@app.route('/configure-airdna', methods=['POST'])
def configure_airdna():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Process and securely store credentials as needed
    set_user_details(username, password)
    print(f"Configured AirDNA credentials: {username} / {password}")
    return jsonify({"message": "AirDNA credentials updated successfully."}), 200

# Route to set Google Maps API key
@app.route('/set-google-maps-key', methods=['POST'])
def set_google_maps_key():
    data = request.get_json()
    api_key = data.get('api_key')
    # Process and securely store the API key as needed
    set_google_maps_api_key(api_key)
    print(f"Google Maps API key set: {api_key}")
    return jsonify({"message": "Google Maps API key updated successfully."}), 200

# Route to download all market names as CSV using send_from_directory
@app.route('/download-markets', methods=['GET'])
def download_markets():
    file = get_markets_as_csv()
    directory, filename = os.path.split(file)
   
    if file:
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        return jsonify({"error": "Market CSV not found."}), 404

# Route to validate market and prepare submarkets CSV
@app.route('/download-submarkets', methods=['POST'])
def download_submarkets():
    data = request.get_json()
    market_input = data.get('market')
    
    # confirm_entered_market should return a tuple (user_pref, details)
    user_pref, details = confirm_entered_market(market_input)
    if not details:
        return jsonify({"error": "Invalid market name. Please enter a valid market."}), 400
    
    # Use the market ID from details, not the raw input.
    csv_status, csv_file = get_submarkets_as_csv(details["market_id"])
    if csv_status == "success":
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Submarkets CSV not found."}), 404

# Separate route to actually send the submarkets CSV file using send_from_directory
@app.route('/download-submarkets-file', methods=['GET'])
def download_submarkets_file():
    # Get the market name from the query parameters
    market_input = request.args.get('market')
    
    # Validate and retrieve market details using confirm_entered_market.
    user_pref, details = confirm_entered_market(market_input)
    if not details:
        return jsonify({"error": "Invalid market name. Please enter a valid market."}), 400
    
    # Use the market ID from details.
    csv_status, csv_file = get_submarkets_as_csv(details["market_id"])
    
    if csv_status == "success" and csv_file and os.path.exists(csv_file):
        directory, filename = os.path.split(csv_file)
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        return jsonify({"error": "Submarkets CSV not found"}), 404


@app.route('/download-file/<file_type>', methods=['GET'])
def download_file(file_type):
    """
    Serves the JSON or CSV file if available.
    The file_type parameter should be either 'json' or 'csv'.
    """
    global completed_json_file, completed_csv_file

    # Validate file_type
    file_type = file_type.lower()
    if file_type not in ['json', 'csv']:
        return jsonify({'error': 'Invalid file type requested.'}), 400

    # Choose file based on type
    file_path = completed_json_file if file_type == 'json' else completed_csv_file

    if file_path and os.path.exists(file_path):
        directory, filename = os.path.split(file_path)
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        return jsonify({'error': f"{file_type.upper()} file not found. Please ensure scraping has completed and the file has been created."}), 404


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Only open the browser if this is the reloader's child process.
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Timer(1, open_browser).start()
    app.run(port=5000, debug=True)

