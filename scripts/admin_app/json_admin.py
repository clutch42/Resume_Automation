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

        # Bottom buttons for saving/loading all tabs
        bottom_buttons = tk.Frame(main_frame)
        bottom_buttons.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        tk.Button(bottom_buttons, text="Load All", command=self.load_all).pack(side=tk.LEFT, padx=10)
        tk.Button(bottom_buttons, text="Save All", command=self.save_all).pack(side=tk.LEFT)
        tk.Button(bottom_buttons, text="New User", command=self.create_new_user).pack(side=tk.LEFT, padx=10)

    def load_all(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(os.path.dirname(script_dir))
        data_dir = os.path.join(project_dir, "data")

        folder = filedialog.askdirectory(title="Select Folder with JSON Files", initialdir=data_dir)
        if not folder:
            return

        # Load personal info
        pi_path = os.path.join(folder, "personal_info.json")
        if os.path.exists(pi_path):
            try:
                with open(pi_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.personal_info_tab.load_data(data)
                    self.personal_info_tab.current_file = pi_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load personal_info.json:\n{e}")

        # Load skills
        skills_path = os.path.join(folder, "skills.json")
        if os.path.exists(skills_path):
            try:
                with open(skills_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.skills_tab.load_data(data)
                    self.skills_tab.current_file = skills_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load skills.json:\n{e}")
        
        # Load certifications
        cert_path = os.path.join(folder, "certifications.json")
        if os.path.exists(cert_path):
            try:
                with open(cert_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.certifications_tab.load_data(data)
                    self.certifications_tab.current_file = cert_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load certifications.json:\n{e}")
            
        # Load education
        edu_path = os.path.join(folder, "education.json")
        if os.path.exists(edu_path):
            try:
                with open(edu_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.education_tab.load_data(data)
                    self.education_tab.current_file = edu_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load education.json:\n{e}")

    def save_all(self):
        # Save personal info
        if self.personal_info_tab.current_file:
            try:
                with open(self.personal_info_tab.current_file, "w", encoding="utf-8") as f:
                    json.dump(self.personal_info_tab.info, f, indent=2)
                print(f"Personal info saved to {self.personal_info_tab.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save personal_info.json:\n{e}")
        else:
            print("No personal_info.json file loaded, skipping save.")

        # Save skills
        if self.skills_tab.current_file:
            try:
                with open(self.skills_tab.current_file, "w", encoding="utf-8") as f:
                    json.dump({
                        cat: [{"name": s["name"], "aliases": s.get("aliases", [])} for s in skills]
                        for cat, skills in self.skills_tab.skills.items()
                    }, f, indent=2)
                print(f"Skills saved to {self.skills_tab.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save skills.json:\n{e}")
        else:
            print("No skills.json file loaded, skipping save.")

        messagebox.showinfo("Save Complete", "All data saved successfully.")

        # Save certifications
        if self.certifications_tab.current_file:
            try:
                with open(self.certifications_tab.current_file, "w", encoding="utf-8") as f:
                    json.dump(self.certifications_tab.certifications, f, indent=2)
                print(f"Certifications saved to {self.certifications_tab.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save certifications.json:\n{e}")
        else:
            print("No certifications.json file loaded, skipping save.")

        # Save education
        if hasattr(self.education_tab, 'current_file') and self.education_tab.current_file:
            try:
                with open(self.education_tab.current_file, "w", encoding="utf-8") as f:
                    json.dump(self.education_tab.get_data(), f, indent=2)
                print(f"Education saved to {self.education_tab.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save education.json:\n{e}")
        else:
            print("No education.json file loaded, skipping save.")


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
