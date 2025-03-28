import googlemaps
import json
import time
from datetime import datetime
from constants import initialize_user_info, get_google_maps_api_key
from googlemaps.exceptions import ApiError, TransportError, Timeout

initialize_user_info()
API_KEY = get_google_maps_api_key()

def fetch_reverse_geocode(api_key, lat, lng, max_retries=5):
    """
    Fetch reverse geocode data with error handling and exponential backoff.

    :param api_key: Google Maps API key
    :param lat: Latitude of the location
    :param lng: Longitude of the location
    :param max_retries: Maximum number of retries for rate limiting or transient errors
    :return: Reverse geocoding result or None if failed
    """
    gmaps = googlemaps.Client(key=api_key)
    retries = 0
    
    while retries < max_retries:
        try:
            result = gmaps.reverse_geocode((lat, lng))
            return result
        # except RateLimitExceeded:
        #     wait_time = 2 ** retries  # Exponential backoff
        #     print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
        #     time.sleep(wait_time)
        except (ApiError, TransportError, Timeout) as e:
            print(f"API error occurred: {e}. Retrying...")
            time.sleep(2 ** retries)
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
        
        retries += 1
    
    print("Max retries reached. Failed to fetch data.")
    return None
def fetch_address(latitude, longitude):
    address = None
    data = fetch_reverse_geocode(API_KEY, latitude, longitude)
    if data:
        address = data[0]["formatted_address"]
    return address
 

def save_to_json(data, file_path):
    """
    Save data to a JSON file.

    :param data: Data to save
    :param file_path: Path to the JSON file
    """
    try:
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data has been saved to {file_path}")
    except Exception as e:
        print(f"Failed to save JSON file: {e}")

# # Example usage
# if __name__ == "__main__":

#     latitude, longitude = 27.8013575, -97.084624
#     file_path = "address_data.json"
    
#     address = fetch_address(latitude, longitude)
#     print(address)
