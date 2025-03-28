import pandas as pd
import json

def save_json_to_csv(json_file):
    csv_file = json_file.replace(".json", ".csv")
    
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        if data:
            df = pd.DataFrame(data)
            df.to_csv(csv_file, index=False, encoding="utf-8")
            
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error: {e}")
    
    

def save_object_to_csv(_object, csv_file):
    try:
        df = pd.DataFrame(_object)
        df.to_csv(csv_file, index=False, encoding="utf-8")
        
    except Exception as e:
        print(f"Error: {e}")
    
    

