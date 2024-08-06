import json
import os
from pprint import pprint

DELIMITER = "-" * 80 + "\n\n"

def load_text_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    
def save_text_to_file(text: str, file_path: str):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
        
def load_json_file(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_json_file(data: dict, file_path: str):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def ensure_dir_exists(*path_parts):
    dir_path = os.path.join(*path_parts)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path
   
def pprint_and_wait(*args):
    for arg in args:
        pprint(arg)
    input("Press Enter to continue...")

def format_model_name(model_name: str) -> str:
    return model_name.split("/")[-1].replace(":", "-")
