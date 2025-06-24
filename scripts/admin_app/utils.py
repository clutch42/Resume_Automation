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

def load_professional_titles(user_folder_path):
    try:
        path = os.path.join(user_folder_path, "summaries.json")
        with open(path, "r", encoding="utf-8") as f:
            summary_map = json.load(f)
        # Exclude "default" from choices
        titles = [title for title in summary_map.keys() if title.lower() != "default"]
        return titles
    except Exception as e:
        print(f"Error loading professional titles: {e}")
        return []

def load_skills(user_folder_path):
    try:
        path = os.path.join(user_folder_path, "skills.json")
        with open(path, "r", encoding="utf-8") as f:
            skills_dict = json.load(f)
        return skills_dict
    except Exception as e:
        print(f"Error loading skills: {e}")
        return {}

def load_experience(user_folder_path):
    try:
        path = os.path.join(user_folder_path, "experience.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading experience data: {e}")
        return []

def load_education(user_folder_path):
    try:
        path = os.path.join(user_folder_path, "education.json")
        with open(path, "r", encoding="utf-8") as f:
            education_list = json.load(f)
        return education_list
    except Exception as e:
        print(f"Error loading education data: {e}")
        return []
    
def load_certifications(user_folder_path):
    try:
        path = os.path.join(user_folder_path, "certifications.json")
        with open(path, "r", encoding="utf-8") as f:
            certifications = json.load(f)
        return certifications
    except Exception as e:
        print(f"Error loading certifications: {e}")
        return []

def load_projects(user_folder_path):
    try:
        path = os.path.join(user_folder_path, "projects.json")
        with open(path, "r", encoding="utf-8") as f:
            projects = json.load(f)
        return projects
    except Exception as e:
        print(f"Error loading projects: {e}")
        return []

def load_personal_info(user_folder_path):
    try:
        path = os.path.join(user_folder_path, "personal_info.json")
        with open(path, "r", encoding="utf-8") as f:
            personal_info = json.load(f)
        return personal_info
    except Exception as e:
        print(f"Error loading personal info: {e}")
        return {}
    
def load_job_description(json_path="../output/output.json"):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading job description: {e}")
        return {}

def load_summary(user_folder_path, professional_title):
    try:
        path = os.path.join(user_folder_path, "summaries.json")
        with open(path, "r", encoding="utf-8") as f:
            summary_map = json.load(f)

        entry = summary_map.get(professional_title) or summary_map.get("default")
        if entry and "summary" in entry:
            summary_path = os.path.join(user_folder_path, entry["summary"])
            with open(summary_path, "r", encoding="utf-8") as sf:
                return sf.read().strip()
    except Exception as e:
        print(f"Error loading summary: {e}")

    return None