import os
import json
from app.data import LANDSCAPE_ITEMS

CUSTOM_DATA_FILE = 'custom_landscape_items.json'

def load_custom_data():
    if os.path.exists(CUSTOM_DATA_FILE):
        with open(CUSTOM_DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        # If the file doesn't exist, create it with the default data
        save_custom_data(LANDSCAPE_ITEMS)
        return LANDSCAPE_ITEMS.copy()

def save_custom_data(data):
    with open(CUSTOM_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def reset_custom_data():
    global CUSTOM_LANDSCAPE_ITEMS
    CUSTOM_LANDSCAPE_ITEMS = LANDSCAPE_ITEMS.copy()
    save_custom_data(CUSTOM_LANDSCAPE_ITEMS)
    return CUSTOM_LANDSCAPE_ITEMS

def update_item_price(category, item_name, new_price, subcategory=None):
    global CUSTOM_LANDSCAPE_ITEMS
    if category in CUSTOM_LANDSCAPE_ITEMS:
        if subcategory:
            if subcategory in CUSTOM_LANDSCAPE_ITEMS[category]:
                for item in CUSTOM_LANDSCAPE_ITEMS[category][subcategory]:
                    if item['name'] == item_name:
                        item['price'] = new_price
                        break
        else:
            for item in CUSTOM_LANDSCAPE_ITEMS[category]:
                if item['name'] == item_name:
                    item['price'] = new_price
                    break
    save_custom_data(CUSTOM_LANDSCAPE_ITEMS)

def remove_custom_item(category, item_name):
    global CUSTOM_LANDSCAPE_ITEMS
    if category in CUSTOM_LANDSCAPE_ITEMS:
        CUSTOM_LANDSCAPE_ITEMS[category] = [item for item in CUSTOM_LANDSCAPE_ITEMS[category] if item['name'] != item_name]
        if not CUSTOM_LANDSCAPE_ITEMS[category]:
            del CUSTOM_LANDSCAPE_ITEMS[category]
        save_custom_data(CUSTOM_LANDSCAPE_ITEMS)



CUSTOM_LANDSCAPE_ITEMS = load_custom_data()