import os
import json
from pathlib import Path
from datetime import datetime


# -------------------- GLOBALS TO SAVE CONFIG --------------------
CONFIG_DIR = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "stash"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config() -> dict:

    '''
    Loads the configuration object from the JSON file
    '''

    if CONFIG_FILE.exists():
        with CONFIG_FILE.open() as config_file:
            return json.load(config_file)
    
    return {}

def save_config(config: dict) -> None:

    '''
    Saves the configuration object to the JSON file
    '''

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w") as config_file:
        json.dump(config, config_file, indent=2)

def create_unique_id(full_name:str, dob: datetime):

    '''
    Create a unique ID by combining full name and dob.
    Example: firstnamelastname_daymonthyear
    '''

    return full_name.replace(" ", "").lower() + "_" + str(dob.day) + str(dob.month) + str(dob.year)

def is_duplicate_account(contents: list, holder_full_name:str, dob: datetime):

    '''
    Checks the given list of contents to see if current account in question already exists in contents.
    Returns True if account already exists contents
    Returns false if account does not exist in contents
    '''

    is_duplicate_id = False

    # Loop through each account
    for account in contents:
        
        # Generate unique ID for current account
        current_acc_id = create_unique_id(holder_full_name, dob)

        # Compare unique IDs
        if current_acc_id == account["id"]:
            is_duplicate_id = True
            break
    
    if not is_duplicate_id:
        # Account is not duplicate
        return False
    else:
        # Account is duplicate
        return True
    


