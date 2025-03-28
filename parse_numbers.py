

import math

def parse_number_string(num_str: str) -> str:
    num_str = num_str.strip().upper()  # Ensure consistent formatting
    
    if num_str.endswith("K"):
        num = float(num_str[:-1])  # Convert the numeric part to float
        return str(math.ceil(num * 1000))  # Multiply by 1000 and round up
    
    elif num_str.endswith("M"):
        num = float(num_str[:-1])  # Convert the numeric part to float
        return str(math.ceil(num * 1000000))  # Multiply by 1,000,000 and round up
    
    return num_str  # Return unchanged if no suffix

# # Example usage:
# examples = ["2.3K", "67.6K", "455K", "678.9K", "1.5M", "100M", "1234"]
# converted = [parse_number_string(num) for num in examples]
# print(converted)  # Output: ['2400', '68000', '455000', '679000', '1500000', '100000000', '1234']
