import tkinter as tk
import os
from utils import save_json_file, load_json_file

class BaseTab:
    def __init__(self, notebook, tab_name, default_filename, autosave_suffix="_autosave.json"):
        self.frame = tk.Frame(notebook)
        notebook.add(self.frame, text=tab_name)

        self.data = None
        self.current_file = None
        self.default_filename = default_filename
        self.autosave_suffix = autosave_suffix

    def load_data(self, data):
        """To be implemented in subclass to update UI from data"""
        raise NotImplementedError

    def get_data(self):
        """To be implemented in subclass to gather data from UI"""
        raise NotImplementedError

    def load(self, folder):
        print("load() method called")
        path = os.path.join(folder, self.default_filename)
        print(f"Trying to load from path: {path}")
        data = load_json_file(path, label=self.default_filename)
        if data is not None:
            self.data = data
            self.current_file = path
            self.load_data(data)

    def save(self):
        if not self.current_file:
            return
        data = self.get_data()
        save_json_file(self.current_file, data, label=self.default_filename)

    def autosave(self):
        if not self.current_file:
            return
        folder = os.path.dirname(self.current_file)
        autosave_path = os.path.join(folder, self.default_filename.replace(".json", self.autosave_suffix))
        data = self.get_data()
        save_json_file(autosave_path, data, label=f"{self.default_filename} (autosave)")
