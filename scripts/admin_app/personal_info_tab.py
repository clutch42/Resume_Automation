import tkinter as tk
from base_tab import BaseTab  # Assuming BaseTab is in base_tab.py

class PersonalInfoTab(BaseTab):
    def __init__(self, notebook):
        super().__init__(notebook, "Personal Info", "personal_info.json")
        
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

    def load_data(self, data):
        if not isinstance(data, dict):
            return
        self.data = data
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, data.get(key, ""))

    def get_data(self):
        result = {}
        for key in self.fields:
            result[key] = self.entries[key].get().strip()
        self.data = result
        return result

    def on_entry_change(self, event=None):
        self.autosave()
