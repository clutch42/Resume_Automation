import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import json
import os
from personal_info_tab import PersonalInfoTab
from skills_tab import SkillsTab
from certifications_tab import CertificationsTab
from education_tab import EducationTab
from experience_tab import ExperienceTab
from projects_tab import ProjectsTab
from summaries_tab import SummariesTab

from utils import LargeEntryDialog

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
        self.experience_tab = ExperienceTab(self.notebook)
        self.projects_tab = ProjectsTab(self.notebook)
        self.summaries_tab = SummariesTab(self.notebook)


        self.files_to_load = [
            ("personal_info.json", self.personal_info_tab, "current_file", {}),
            ("skills.json", self.skills_tab, "current_file", {}),
            ("certifications.json", self.certifications_tab, "current_file", []),
            ("education.json", self.education_tab, "current_file", []),
            ("experience.json", self.experience_tab, "current_file", []),
            ("projects.json", self.projects_tab, "current_file", {}),
            ("summaries.json", self.summaries_tab, "current_file", {}),
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

        for filename, tab, attr, _ in self.files_to_load:
            path = os.path.join(folder, filename)
            self.load_json_file(path, tab, attr, filename)

    def save_all(self):
        for filename, tab, file_attr, _ in self.files_to_load:
            if getattr(tab, file_attr):
                tab.save()
            else:
                print(f"No {filename} file loaded, skipping save.")
        messagebox.showinfo("Save Complete", "All data saved successfully.")

    def create_new_user(self):
        dlg = LargeEntryDialog(self.root, title="New User", prompt="Enter new user name:")
        user_name = dlg.result
        if not user_name:
            return

        user_name = user_name.strip()
        if not user_name:
            messagebox.showerror("Error", "User name cannot be empty.")
            return

        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(os.path.dirname(script_dir))
        data_dir = os.path.join(project_dir, "data")

        user_folder = os.path.join(data_dir, user_name)
        if os.path.exists(user_folder):
            messagebox.showerror("Error", f"User folder '{user_name}' already exists.")
            return

        try:
            os.makedirs(user_folder, exist_ok=False)

            for filename, tab_obj, file_attr, default_data in self.files_to_load:
                path = os.path.join(user_folder, filename)
                # Special handling for summaries.json
                if filename == "summaries.json":
                    summaries_folder = os.path.join(user_folder, "summaries")
                    os.makedirs(summaries_folder, exist_ok=True)
                    
                    default_txt_path = os.path.join(summaries_folder, "default.txt")
                    if not os.path.exists(default_txt_path):
                        with open(default_txt_path, "w", encoding="utf-8") as f:
                            f.write("Default summary content here.")  # or ""

                    # Prepare default summaries data with paths inside summaries folder
                    summaries_with_paths = {}
                    for key in default_data:
                        file_name = key.lower().replace(" ", "_") + ".txt"
                        summaries_with_paths[key] = os.path.join("summaries", file_name)
                        
                        # Create empty summary text file
                        summary_txt_path = os.path.join(user_folder, summaries_with_paths[key])
                        if not os.path.exists(summary_txt_path):
                            with open(summary_txt_path, "w", encoding="utf-8") as f:
                                f.write("")

                    summaries_with_paths["default"] = "summaries/default.txt"

                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(summaries_with_paths, f, indent=2)
                    
                    tab_obj.load_data(summaries_with_paths)
                    setattr(tab_obj, file_attr, path)
                    continue  # Skip to next file after summaries is handled
                
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(default_data, f, indent=2)
                tab_obj.load_data(default_data)
                setattr(tab_obj, file_attr, path)

            messagebox.showinfo("Success", f"New user '{user_name}' created and loaded.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create new user folder:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SkillManagerApp(root)
    root.geometry("1000x600")
    root.mainloop()
