import os
from os import path


base_dir = os.path.join(os.path.expanduser("~"), "Documents", "Airbnb_Airdna_Tool_App_Data")

os.makedirs(base_dir, exist_ok=True)

# Make sure all folders exist:
market_csv_dir = os.path.join(base_dir, "markets_csv")
os.makedirs(market_csv_dir, exist_ok=True)
listings_json_dir = os.path.join(base_dir, "listings_json")
os.makedirs(listings_json_dir, exist_ok=True)
submarket_listings_dir = os.path.join(base_dir, "submarket_listings")
os.makedirs(submarket_listings_dir, exist_ok=True)
market_listings_dir = os.path.join(base_dir, "market_listings")
os.makedirs(market_listings_dir, exist_ok=True)
submarkets_csv_dir = os.path.join(base_dir, "submarkets_csv")
os.makedirs(submarkets_csv_dir, exist_ok=True)



