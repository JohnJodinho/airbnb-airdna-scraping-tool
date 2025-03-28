import re
import json

# get user input and cofrim it, then return the market
def confirm_entered_market(user_enetered_market):
    # COnvere the user entered market to lowercase
    user_enetered_market = user_enetered_market.strip().lower()
    # Check if the user entered market is in the market list

    with open("markets.json", "r", encoding="utf-8") as file:
        markets = json.load(file)
    
    if user_enetered_market.find("/") != -1:
        market_name = user_enetered_market.split("/")[0]
        sub_market_name = user_enetered_market.split("/")[-1]

        for market in markets:
            if re.search(re.escape(market_name), market['parent_market_name'].lower()):
                for sub_market in market["submarket"]:
                    if re.search(re.escape(sub_market_name), sub_market['name'].lower()):
                        return "sub_market", sub_market
        return "sub_market", {}
    else:
        for market in markets:
            # use regex to check if the user entered market is in the market list
            if re.search(re.escape(user_enetered_market), market['parent_market_name'].lower()):
                return "market", dict(list(market.items())[:3])
        return "market", {}


# Test
# user_input = input("Enter a market location: ")
# result = confirm_entered_market(user_input)
# if result[1]:
#     print(f"User wants a {result[0]}")
#     print(result[1])
# else:
#     print("Market not found")
    
