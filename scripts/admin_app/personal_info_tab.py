import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json
import os

class PersonalInfoTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook)
        notebook.add(self.frame, text="Personal Info")

        self.info = {}
        self.current_file = None

        self.fields = {
            "name": "Name",
            "phone": "Phone",
            "email": "Email",
            "location": "Location",
            "linkedin": "LinkedIn URL",
            "github": "GitHub URL",
            "portfolio": "Portfolio URL"
        }

        self.entries = {}

        form_frame = tk.Frame(self.frame)
        form_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        for i, (key, label_text) in enumerate(self.fields.items()):
            tk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky="w", pady=5)
            entry = tk.Entry(form_frame, width=60)
            entry.grid(row=i, column=1, pady=5, sticky="ew")
            self.entries[key] = entry

        for entry in self.entries.values():
            entry.bind("<FocusOut>", self.on_entry_change)

    def on_entry_change(self, event=None):
        # Update self.info with current entries, and autosave
        for key in self.fields:
            self.info[key] = self.entries[key].get().strip()
        self.autosave()

    def autosave(self):
        try:
            if self.current_file:
                folder = os.path.dirname(self.current_file)
            else:
                # fallback to default data folder if no file loaded yet
                script_dir = os.path.dirname(os.path.abspath(__file__))
                project_dir = os.path.dirname(os.path.dirname(script_dir))
                folder = os.path.join(project_dir, "data")
                os.makedirs(folder, exist_ok=True)

            path = os.path.join(folder, "personal_info_autosave.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.info, f, indent=2)
            print(f"Personal info autosaved to {path}")
        except Exception as e:
            print(f"Autosave failed: {e}")

    def load_data(self, data):
        if not isinstance(data, dict):
            return
        self.info = data
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, data.get(key, ""))