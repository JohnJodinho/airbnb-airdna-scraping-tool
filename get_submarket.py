import requests
import json
import zstandard as zstd
import time
import os

def save_cookies_to_file(cookies, filename):
    """Save cookies to a JSON file."""
    with open(filename, "w") as f:
        json.dump(cookies, f, indent=4)

def load_cookies_from_file(filename):
    """Load cookies from a JSON file."""
    with open(filename, "r") as f:
        return json.load(f)
import json

def process_market_data(sub_market=None):
    if sub_market:
        
    
        submarkets = sub_market["payload"]["submarkets"]
        market_dict = {}
        
        # Step 1: Extract unique market_id and corresponding parent_market_name
        for submarket in submarkets:
            market_id = submarket["market_id"]
            parent_market_name = submarket["parent_market_name"]
            
            if market_id not in market_dict:
                market_dict[market_id] = {
                    "market_id": market_id,
                    "parent_market_name": parent_market_name,
                    "market_url": f"https://app.airdna.co/data/us/{market_id}",
                    "submarket": []
                }
        
        # Convert market_dict values to a list
        market_list = list(market_dict.values())
        
        # Step 2: Populate the submarket list
        for market in market_list:
            market_id = market["market_id"]
            
            for submarket in submarkets:
                if submarket["market_id"] == market_id:
                    submarket_data = {
                        "id": submarket["id"],
                        "name": submarket["name"],
                        "submarket_url": f"https://app.airdna.co/data/us/{market_id}/{submarket['id']}"
                    }
                    market["submarket"].append(submarket_data)
        
        return market_list


def get_sub_markets(country_code):
    last_message = ""
    url = f"https://api.airdna.co/api/explorer/v1/country/{country_code}/submarkets"

    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "origin": "https://app.airdna.co",
        "referer": "https://app.airdna.co/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # "x-requested-with": "disableCaseConversion"

    }

    payload = {"filters":[],"sort_order":"market_score","currency":"usd","pagination":{"page_size":7000,"offset":0},"compute_metrcs":True}

    cookies = {
    "intercom-id-kgkrrbqi": "d3c51718-d91c-4d01-b2a7-8f48a5eb4a92",
    "intercom-device-id-kgkrrbqi": "4e87203e-deac-4468-b45c-72b992199364",
    "_ga_H6TECFYJBJ": "GS1.1.1734482385.1.1.1734482813.0.0.0",
    "ajs_anonymous_id": "e4d55169-4364-41dd-8463-89797f13c0b8",
    "_fbp": "fb.1.1734483236515.258659550926446679",
    "__adroll_fpc": "9c84a1369f01a41b58e940e49ff1410e-1734483241007",
    "hubspotutk": "d282e163bceb237ff70446ecf7e590ff",
    "_hjSessionUser_71262": "eyJpZCI6IjQyZDExOTc3LWI1ZjktNTc5MS04YjdmLTlmNDU4YjE0MzVkNSIsImNyZWF0ZWQiOjE3MzQ0ODMyMzUwMjYsImV4aXN0aW5nIjp0cnVlfQ==",
    "ajs_user_id": "876317",
    "_vwo_uuid_v2": "DA8CAADA3B8E60D9170A987269D3C263E|11763880d617dd7658806b98350c5672",
    "_vwo_uuid": "DA8CAADA3B8E60D9170A987269D3C263E",
    "_vis_opt_exp_13_combi": "2",
    "_vis_opt_exp_5_combi": "2",
    "idr-token": "YVI_XZyuHAUeLeomm6NohWkgszuMj3Zr3HBApEdcENJ9AaU3gID8Dw",
    "_vis_opt_exp_11_combi": "3",
    "_ga": "GA1.1.1225357084.1734482386",
    "_ga_EQ37P58RZZ": "GS1.1.1740962755.3.1.1740964739.60.0.0",
    "_vwo_ds": "3%241742263539%3A51.09967463%3A%3A",
    "_gcl_au": "1.1.133162551.1742263544",
    "mmm-cookie": "ODc2MzE3|a365b63f333d4e0ba2f63365533c34f5",
    "_vis_opt_s": "15%7C",
    "_vis_opt_test_cookie": "1",
    "amplitude_idundefinedairdna.co": "eyJvcHRPdXQiOmZhbHNlLCJzZXNzaW9uSWQiOm51bGwsImxhc3RFdmVudFRpbWUiOm51bGwsImV2ZW50SWQiOjAsImlkZW50aWZ5SWQiOjAsInNlcXVlbmNlTnVtYmVyIjowfQ==",
    "_hjSession_71262": "eyJpZCI6ImJlMzkyZjFiLTZiNmItNDllYi04NzA4LTg5YTI5OTIwYjZlZiIsImMiOjE3NDIzNTM3MTE1OTAsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=",
    "__hstc": "265997264.d282e163bceb237ff70446ecf7e590ff.1734483247126.1742263604903.1742353753425.27",
    "__hssrc": "1",
    "amplitude_id_24ef8c5734b56d203283d7fa4245d68eairdna.co": "eyJkZXZpY2VJZCI6IjVhMjA2MmFiLTRiNGQtNDUwNC05ODY3LWQ2NzZjNDJkY2Y5MFIiLCJ1c2VySWQiOiI4NzYzMTciLCJvcHRPdXQiOmZhbHNlLCJzZXNzaW9uSWQiOjE3NDIzNTM3MTEwMzQsImxhc3RFdmVudFRpbWUiOjE3NDIzNTQyNDI4MDMsImV2ZW50SWQiOjg5OCwiaWRlbnRpZnlJZCI6MjI4LCJzZXF1ZW5jZU51bWJlciI6MTEyNn0=",
    "__hssc": "265997264.2.1742353753425",
    "intercom-session-kgkrrbqi": "V3d5WGNGbkJieFFHL21tQzZzQUticndvWFlDVUt0N0J0c1JYa2F1Z0NwMllOazd1YmpMcVJ0NXhrRVlNNXdFS3RSL0IvNEljbitxWjYvVDlHR2l5end2LzVHcG5Wam5iOGU4K09YeHZaVWs9LS1neFVzVGlDVE1DQzB1RGkvRE9KM0pRPT0=--a2d740efe4bb777c8684b10976acc68e35fa18f8",
    "_ga_13DRG885CK": "GS1.1.1742353714.34.1.1742354363.0.0.0",
    "_ga_QJS7VP5707": "GS1.1.1742353713.30.1.1742354364.24.0.0",
    "id-token": "eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCIsImtpZCI6Ii1xRUFDM1daM2hPNWoxWlZISWRBQ252c01yQmt1YmxHIn0.eyJhdWQiOiI1ZjA0MDQ2NC0wYWVmLTQ4YTEtYTFkMS1kYWE5ZmJmODE0MTUiLCJleHAiOjE3NDIzNTc5ODksImlhdCI6MTc0MjM1NDM4OSwiaXNzIjoicHJvZC5haXJkbmEuY28iLCJzdWIiOiIxNGU5NzExMS04ZmZkLTRkODYtODU3ZS1hZjNjZjgwODI0OTEiLCJqdGkiOiI0MzUwNGYxMi01N2M3LTQ5ZjgtYWI0MC0zM2QyM2Q3YzgyODEiLCJhdXRoZW50aWNhdGlvblR5cGUiOiJSRUZSRVNIX1RPS0VOIiwiZW1haWwiOiJtYXJrQHdlc3Rjb2FzdGhvbWVzdGF5cy5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicHJlZmVycmVkX3VzZXJuYW1lIjoibWFya0B3ZXN0Y29hc3Rob21lc3RheXMuY29tIiwiYXBwbGljYXRpb25JZCI6IjVmMDQwNDY0LTBhZWYtNDhhMS1hMWQxLWRhYTlmYmY4MTQxNSIsInRpZCI6IjFmYjIwNmE4LTE3N2ItNDY4NC1hZjFmLThmZmY3Y2MxNTNhMCIsInJvbGVzIjpbIlVzZXIiXSwiYXV0aF90aW1lIjoxNzM5ODg0OTUyLCJzaWQiOiJiYmYxOGU4Ny1hMjY1LTQ2YTctYjc2Zi0zODNhODVhYjYwZjkifQ.by2962XhhS2tN_0YKxTAuJ9gNxP_dSDXlDouy0rQvumW1IsgWa710DuSrO-ZQOUY",
    "mmm-access-jwt-cookie": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbmNvZGVkX2FjY2Vzc190b2tlbiI6ImEzNjViNjNmMzMzZDRlMGJhMmY2MzM2NTUzM2MzNGY1IiwiZXhwIjoxNzQyNDQwNzg5LCJwZXJtaXNzaW9ucyI6eyJjaXR5IjpbNTkwNTNdLCJyZWdpb24iOltdLCJjb3VudHJ5IjpbXSwic3RhdGUiOltdLCJ3b3JsZCI6ZmFsc2V9fQ.1vllHP0oIN9pWWYFucr3xk5KxD1cel7znr-Uj6mBUco",
    "mmm-access-jwt-refresh-cookie": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbmNvZGVkX2FjY2Vzc190b2tlbiI6ImEzNjViNjNmMzMzZDRlMGJhMmY2MzM2NTUzM2MzNGY1IiwiZXhwIjoxNzQ0OTQ2Mzg5fQ.NpBhQTFbuaRwK6HX4dUSt72qtewp4CqcVpImouhP5ko",
    "mm-csrf": "a9f313d1cfe61d5c4b25a15b646b782d2b63c3f995f43334b6fae126856d9487",
    "_uetsid": "6bfad5e0046f11f0a35e01c77c862a42",
    "_uetvid": "8ecdda90bcda11efac4365622627efb9",
    "_vwo_sn": "90165%3A12%3A%3A%3A1"
    }

    max_retries = 5

    session = requests.Session()
    
    for retries in range(max_retries):
        try:
            # Check if market_cookies.json exists
            cookies_json = "sub_market_cookies.json"

            if os.path.exists(cookies_json):
                print("Loading cookies from file...")
                cookies_dict = load_cookies_from_file(cookies_json)
                response = session.post(url, headers=headers, cookies=cookies_dict, json=payload)
            
            else:
                print("Fetching new session cookies...")
                response = session.post(url, headers=headers, cookies=cookies, json=payload)
                # Store session cookies in a dictionary
                cookies_dict = session.cookies.get_dict() 
                # Save cookies to file
                save_cookies_to_file(cookies, cookies_json)

            # Handle response
            if response.status_code == 200:

                json_data = response.json()
                
                json_data = process_market_data(json_data)
       
                with open("markets.json", "w", encoding="utf-8") as file:
                    json.dump(json_data, file, indent=4)
                
                print("JSON response saved successfully.")
                last_message = "Success"
                
            else:
                print(f"Request failed with status code {response.status_code}")
                print(response.text)
                last_message = "failure"
                continue
            
            break
        except Exception as e:
            print(f"Error getting markets: {e}")
            time.sleep(retries * 2)
            if max_retries == retries+1:
                print("Max retries reached. Exiting...")
                last_message = "failure"
    return last_message
        

