import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog

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

class LargeEntryDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, prompt="Enter:", initialvalue="", width=50, height=10):
        self.prompt = prompt
        self.initialvalue = initialvalue
        self.width = width
        self.height = height
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text=self.prompt).pack(padx=5, pady=5)
        self.entry = tk.Text(master, width=self.width, height=self.height)  # Bigger text widget
        self.entry.pack(padx=5, pady=5)
        self.entry.insert("1.0", self.initialvalue)
        return self.entry

    def apply(self):
        self.result = self.entry.get("1.0", tk.END).strip()