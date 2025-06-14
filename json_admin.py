import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json
import os

class SkillManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Skill Categories Manager")

        self.skills = {}  # {category: [skills]}
        self.current_file = None
        self.last_selected_category = None  # Tracks last selected category

        # Left frame: Categories list + buttons
        left_frame = tk.Frame(root)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(left_frame, text="Categories").pack()
        self.category_listbox = tk.Listbox(left_frame, width=40)
        self.category_listbox.pack(fill=tk.Y, expand=True)
        self.category_listbox.bind("<<ListboxSelect>>", self.on_category_select)

        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Category", command=self.add_category).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Delete Category", command=self.delete_category).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Rename Category", command=self.rename_category).pack(side=tk.LEFT)

        # Right frame: Skills list + buttons
        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(right_frame, text="Skills in Category").pack()
        self.skills_listbox = tk.Listbox(right_frame, width=40)
        self.skills_listbox.pack(fill=tk.BOTH, expand=True)

        skills_btn_frame = tk.Frame(right_frame)
        skills_btn_frame.pack(pady=5)
        tk.Button(skills_btn_frame, text="Add Skill", command=self.add_skill).pack(side=tk.LEFT)
        tk.Button(skills_btn_frame, text="Delete Skill", command=self.delete_skill).pack(side=tk.LEFT)
        tk.Button(skills_btn_frame, text="Rename Skill", command=self.rename_skill).pack(side=tk.LEFT)

        # Bottom frame: Load and Save buttons
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        tk.Button(bottom_frame, text="Load JSON", command=self.load_json).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="Save JSON", command=self.save_json).pack(side=tk.LEFT, padx=5)

    def add_category(self):
        new_cat = simpledialog.askstring("Add Category", "Enter new category name:")
        if new_cat:
            new_cat = new_cat.strip()
            if new_cat in self.skills:
                messagebox.showerror("Error", "Category already exists.")
            else:
                self.skills[new_cat] = []
                self.refresh_categories()
                self.category_listbox.selection_clear(0, tk.END)
                idx = list(sorted(self.skills.keys())).index(new_cat)
                self.category_listbox.selection_set(idx)
                self.on_category_select()
        self.autosave()

    def delete_category(self):
        sel = self.category_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Please select a category to delete.")
            return
        cat = self.category_listbox.get(sel)
        if messagebox.askyesno("Confirm", f"Delete category '{cat}'? This will remove all its skills."):
            del self.skills[cat]
            self.refresh_categories()
            self.skills_listbox.delete(0, tk.END)
        self.autosave()

    def add_skill(self):
        sel = self.category_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a category first.")
            return
        cat = self.category_listbox.get(sel[0])
        new_skill = simpledialog.askstring("Add Skill", f"Enter new skill for '{cat}':")
        if new_skill:
            new_skill = new_skill.strip()
            if new_skill in self.skills[cat]:
                messagebox.showerror("Error", "Skill already exists in this category.")
            else:
                self.skills[cat].append(new_skill)
                self.refresh_skills(cat)
        self.autosave()

    def delete_skill(self):
        skill_sel = self.skills_listbox.curselection()
        print(f"Skill selection: {skill_sel}")
        if not self.last_selected_category or not skill_sel:
            messagebox.showinfo("Info", "Select a skill to delete.")
            return

        cat = self.last_selected_category
        skill = self.skills_listbox.get(skill_sel[0])

        if messagebox.askyesno("Confirm", f"Delete skill '{skill}' from '{cat}'?"):
            self.skills[cat].remove(skill)
            self.refresh_skills(cat)
        self.autosave()

    def rename_category(self):
        sel = self.category_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Please select a category to rename.")
            return
        old_cat = self.category_listbox.get(sel[0])
        new_cat = simpledialog.askstring("Rename Category", f"Enter new name for category '{old_cat}':")
        if new_cat:
            new_cat = new_cat.strip()
            if new_cat == old_cat:
                return  # no change
            if new_cat in self.skills:
                messagebox.showerror("Error", "Category name already exists.")
                return
            # Rename in the skills dict
            self.skills[new_cat] = self.skills.pop(old_cat)
            self.refresh_categories()
            # Select the renamed category
            idx = list(sorted(self.skills.keys())).index(new_cat)
            self.category_listbox.selection_clear(0, tk.END)
            self.category_listbox.selection_set(idx)
            self.on_category_select()
            self.autosave()

    def rename_skill(self):
        cat_sel = self.category_listbox.curselection()
        skill_sel = self.skills_listbox.curselection()
        if not cat_sel:
            messagebox.showinfo("Info", "Please select a category first.")
            return
        if not skill_sel:
            messagebox.showinfo("Info", "Please select a skill to rename.")
            return
        cat = self.category_listbox.get(cat_sel[0])
        old_skill = self.skills_listbox.get(skill_sel[0])
        new_skill = simpledialog.askstring("Rename Skill", f"Enter new name for skill '{old_skill}':")
        if new_skill:
            new_skill = new_skill.strip()
            if new_skill == old_skill:
                return  # no change
            if new_skill in self.skills[cat]:
                messagebox.showerror("Error", "Skill already exists in this category.")
                return
            idx = self.skills[cat].index(old_skill)
            self.skills[cat][idx] = new_skill
            self.refresh_skills(cat)
            # Select renamed skill
            self.skills_listbox.selection_clear(0, tk.END)
            skill_idx = sorted(self.skills[cat]).index(new_skill)
            self.skills_listbox.selection_set(skill_idx)
            self.autosave()

    def refresh_categories(self):
        self.category_listbox.delete(0, tk.END)
        for cat in sorted(self.skills.keys()):
            self.category_listbox.insert(tk.END, cat)

    def refresh_skills(self, category):
        self.skills_listbox.delete(0, tk.END)
        for skill in sorted(self.skills.get(category, [])):
            self.skills_listbox.insert(tk.END, skill)

    def on_category_select(self, event=None):
        sel = self.category_listbox.curselection()
        if not sel:
            return
        cat = self.category_listbox.get(sel[0])
        self.last_selected_category = cat
        self.refresh_skills(cat)

    def load_json(self, event=None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = filedialog.askopenfilename(
            title="Select JSON file to load",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=script_dir
        )
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.skills = data
                    self.refresh_categories()
                    self.skills_listbox.delete(0, tk.END)
                    self.current_file = filename
                    messagebox.showinfo("Loaded", f"Skills loaded from {filename}")
                else:
                    messagebox.showerror("Error", "Invalid data format in JSON.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{e}")
        else:
            print("No file selected")

    def save_json(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="skills.json"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.skills, f, indent=2)
            self.current_file = path
            messagebox.showinfo("Saved", f"Skills saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save JSON:\n{e}")

    def autosave(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            autosave_path = os.path.join(script_dir, "skills_autosave.json")
            with open(autosave_path, "w", encoding="utf-8") as f:
                json.dump(self.skills, f, indent=2)
            print(f"Autosaved to {autosave_path}")
        except Exception as e:
            print(f"Autosave failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SkillManagerApp(root)
    root.geometry("1000x600")
    root.mainloop()
