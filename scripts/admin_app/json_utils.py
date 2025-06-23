import json
import os
from tkinter import messagebox

def save_json_file(path, data, label=None):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        if label:
            print(f"{label} saved to {path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save {label or path}:\n{e}")

def load_json_file(path, label=None):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            print(f"Loading JSON from: {path}")
            data = json.load(f)
        return data
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load {label or path}:\n{e}")
        return None
