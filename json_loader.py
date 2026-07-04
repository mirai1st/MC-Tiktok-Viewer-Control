import json

def load_json():
    try:
        with open('gift.json', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("Config file not found.")
        return {}