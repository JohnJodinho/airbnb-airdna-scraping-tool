from airbnb_get_json import extract_script_json
from get_address_google import fetch_address

def process_airbnb_data(airbnb_dict):
    final_data = {}
    airbnb_id = airbnb_dict.get("airbnb_property_id")
    airbnb_url = f"https://www.airbnb.com/rooms/{airbnb_id}"
    bedrooms = airbnb_dict.get("bedrooms")
    bathrooms = airbnb_dict.get("bathrooms")
    guests = airbnb_dict.get("accommodates")
    rating = airbnb_dict.get("rating")
    reviews = airbnb_dict.get("reviews")
    title = airbnb_dict.get("title")
    rev_potential = airbnb_dict.get("revenue_potential_ltm")
    market_name = airbnb_dict.get("market_name")
    latitude = airbnb_dict.get("location").get("lat")
    longitude = airbnb_dict.get("location").get("lng")
    the_license = None
    manager = None
    address = None

    result = extract_script_json(airbnb_url)
    if result[0] == "success":
        
        data = result[2]
        
        try:
            sections = data["niobeMinimalClientData"][0][1]["data"]["presentation"]["stayProductDetailPage"]['sections']
        except KeyError:
            sections = None
        except IndexError:
            sections = None
        except TypeError:
            sections = None
        except Exception as e:
            sections = None
            print(f"Error: {e}")
        if sections:

            # Latittude and Longitude
            try:
                latitude = sections["metadata"]["loggingContext"]["eventDataLogging"]["listingLat"]
            except Exception as e:
                latitude = None
                print(f"Error: {e}")
            if latitude is None:
                try:
                    latitude = sections[1]["section"]["lat"]
                except Exception as e:
                    latitude = None
                    print(f"Error: {e}")
            try:
                longitude = sections["metadata"]["loggingContext"]["eventDataLogging"]["listingLng"]
            except Exception as e:
                longitude = None
                print(f"Error: {e}")
            if longitude is None:
                try:
                    longitude = sections[1]["section"]["lng"]
                except Exception as e:
                    longitude = None
                    print(f"Error: {e}")
            try:
                within_sections = sections["sections"]
                for section in within_sections:
                    try:
                        the_license = section["section"]["items"][3]["html"]["htmlText"]
                        
                        break
                    except Exception as e:
                        continue
                        
                  
            except Exception as e:
                the_license = None
                print(f"Error: {e}")
            if the_license is not None and len(the_license) > 25:
                the_license = None
            if the_license is None:
                try:
                    within_sections = sections["sections"]
                    for section in within_sections:
                        try:
                            the_license = section["section"]["policyNumber"]
                            the_license = the_license.replace("Registration number: ", "")
                            break
                        except Exception as e:
                            continue

                    
                except Exception as e:
                    the_license = None
                    print(f"Error: {e}")
            try:
                within_sections = sections["sections"]
                for section in within_sections:
                    try:
                        manager = section["section"]["cardData"]["name"]
                        break
                    except Exception as e:
                        continue
            except Exception as e:
                manager = None
                print(f"Error: {e}")

   
    if isinstance(latitude, float) and isinstance(longitude, float):
        try:
            if address == None:
                address = fetch_address(latitude, longitude)


        except Exception as e:
            print(f"Error: {e}")

    final_data["title"] = title
    final_data["airbnb_url"] = airbnb_url   
    final_data["bedrooms"] = bedrooms
    final_data["bathrooms"] = bathrooms
    final_data["guests"] = guests
    final_data["rating"] = rating
    final_data["reviews"] = reviews
    final_data["vrbo_url"] = None
    final_data["revenue potential"] = rev_potential
    final_data["market name"] = market_name
    # final_data["latitude"] = latitude
    # final_data["longitude"] = longitude
    final_data["license"] = the_license
    final_data["manager"] = manager
    final_data["address"] = address

    return final_data
        


           
            
