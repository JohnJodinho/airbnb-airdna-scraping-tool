import json
import os
import time
from logger_util import custom_print, log_messages

BLOCK_RESOURCE_TYPES = [
  'beacon',
  'csp_report',
  'font',
  'image',
  'imageset',
  'media',
  'object',
  'texttrack'
]

BLOCK_RESOURCE_NAMES = [
  'adzerk',
  'analytics',
  'cdn.api.twitter',
  'doubleclick',
  'exelator',
  'facebook',
  'fontawesome',
  'google',
  'google-analytics',
  'googletagmanager'
]



DEFAULT_USER_INFO = {
    "user_name": "",
    "user_password": "",
    "api_key": ""
}


def initialize_user_info():
    """Creates the user_info.json file with default values if it does not exist 
    and returns initialization status messages."""
    
    if not os.path.exists("user_info.json"):
        custom_print("Initializing user info...")
        

        with open("user_info.json", "w", encoding="utf-8") as file:
            json.dump(DEFAULT_USER_INFO, file, indent=4)
        
        statements = {
            0: "AirDNA username initialized",
            1: "AirDNA password initialized",
            2: "Google Maps API key initialized"
        }
        for step in range(3):
            time.sleep(1)
            custom_print(statements[step])
        
    
    


def set_user_details(username, password):
    """Updates the username and password in user_info.json."""
    with open("user_info.json", "r+", encoding="utf-8") as file:
        data = json.load(file)
        data["user_name"] = username
        data["user_password"] = password
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()


def get_user_details():
    """Retrieves the stored username and password."""
    with open("user_info.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["user_name"], data["user_password"]


def set_google_maps_api_key(api_key):
    """Updates the Google Maps API key in user_info.json."""
    with open("user_info.json", "r+", encoding="utf-8") as file:
        data = json.load(file)
        data["api_key"] = api_key
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()


def get_google_maps_api_key():
    """Retrieves the stored Google Maps API key."""
    with open("user_info.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["api_key"]


