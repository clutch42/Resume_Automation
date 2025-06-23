import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import json
import os
from personal_info_tab import PersonalInfoTab
from skills_tab import SkillsTab
from certifications_tab import CertificationsTab
from education_tab import EducationTab

class SkillManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Skill Categories Manager")

        # Outer frame to hold notebook and bottom buttons
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create Tabs
        self.personal_info_tab = PersonalInfoTab(self.notebook)
        self.skills_tab = SkillsTab(self.notebook)
        self.certifications_tab = CertificationsTab(self.notebook)
        self.education_tab = EducationTab(self.notebook)

        self.files_to_load = [
            ("personal_info.json", self.personal_info_tab, "current_file"),
            ("skills.json", self.skills_tab, "current_file"),
            ("certifications.json", self.certifications_tab, "current_file"),
            ("education.json", self.education_tab, "current_file"),
        ]

        # Bottom buttons for saving/loading all tabs
        bottom_buttons = tk.Frame(main_frame)
        bottom_buttons.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        tk.Button(bottom_buttons, text="Load User", command=self.load_all).pack(side=tk.LEFT, padx=10)
        tk.Button(bottom_buttons, text="Save User", command=self.save_all).pack(side=tk.LEFT)
        tk.Button(bottom_buttons, text="New User", command=self.create_new_user).pack(side=tk.LEFT, padx=10)

    def load_json_file(self, path, tab, attribute_name, label):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    tab.load_data(data)
                    setattr(tab, attribute_name, path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {label}:\n{e}")

    def load_all(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(os.path.dirname(script_dir))
        data_dir = os.path.join(project_dir, "data")

        folder = filedialog.askdirectory(title="Select Folder with JSON Files", initialdir=data_dir)
        if not folder:
            return

        for filename, tab, attr in self.files_to_load:
            path = os.path.join(folder, filename)
            self.load_json_file(path, tab, attr, filename)

    def save_json_file(self, path, data, label):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"{label} saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save {label}:\n{e}")

    def save_all(self):
        # Save personal info
        if self.personal_info_tab.current_file:
            self.save_json_file(self.personal_info_tab.current_file, self.personal_info_tab.data, "personal_info.json")
        else:
            print("No personal_info.json file loaded, skipping save.")

        # Save skills
        if self.skills_tab.current_file:
            skills_data = {
                cat: [{"name": s["name"], "aliases": s.get("aliases", [])} for s in skills]
                for cat, skills in self.skills_tab.skills.items()
            }
            self.save_json_file(self.skills_tab.current_file, skills_data, "skills.json")
        else:
            print("No skills.json file loaded, skipping save.")

        # Save certifications
        if self.certifications_tab.current_file:
            self.save_json_file(self.certifications_tab.current_file, self.certifications_tab.certifications, "certifications.json")
        else:
            print("No certifications.json file loaded, skipping save.")

        # Save education
        if self.education_tab.current_file:
            self.save_json_file(self.education_tab.current_file, self.education_tab.get_data(), "education.json")
        else:
            print("No education.json file loaded, skipping save.")

        messagebox.showinfo("Save Complete", "All data saved successfully.")

    def create_new_user(self):
        # Ask for the new user name
        user_name = simpledialog.askstring("New User", "Enter new user name:")
        if not user_name:
            return  # User cancelled or empty input

        # Sanitize the folder name a bit (strip spaces)
        user_name = user_name.strip()
        if not user_name:
            messagebox.showerror("Error", "User name cannot be empty.")
            return

        # Determine the base data directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(os.path.dirname(script_dir))
        data_dir = os.path.join(project_dir, "data")

        # New user folder path
        user_folder = os.path.join(data_dir, user_name)
        if os.path.exists(user_folder):
            messagebox.showerror("Error", f"User folder '{user_name}' already exists.")
            return

        try:
            # Create new user folder
            os.makedirs(user_folder, exist_ok=False)

            # Create empty personal_info.json with default empty structure
            personal_info_path = os.path.join(user_folder, "personal_info.json")
            with open(personal_info_path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

            # Create empty skills.json with default empty structure
            skills_path = os.path.join(user_folder, "skills.json")
            with open(skills_path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

            # Create empty certifications.json
            certifications_path = os.path.join(user_folder, "certifications.json")
            with open(certifications_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

            # Create empty education.json
            education_path = os.path.join(user_folder, "education.json")
            with open(education_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)  # assuming education data is a list

            # Load these new empty files into the app
            self.personal_info_tab.load_data({})
            self.personal_info_tab.current_file = personal_info_path

            self.skills_tab.load_data({})
            self.skills_tab.current_file = skills_path

            self.certifications_tab.load_data({})
            self.certifications_tab.current_file = certifications_path

            self.education_tab.load_data([])
            self.education_tab.current_file = education_path

            messagebox.showinfo("Success", f"New user '{user_name}' created and loaded.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create new user folder:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SkillManagerApp(root)
    root.geometry("1000x600")
    root.mainloop()
