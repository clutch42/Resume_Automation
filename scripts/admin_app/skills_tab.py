import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json
import os

class SkillsTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook)
        notebook.add(self.frame, text="Skills")

        self.skills = {}
        self.current_file = None
        self.last_selected_category = None
        self.last_selected_skill_index = None
        self.last_selected_skill = None

        self.build_ui()

    def build_ui(self):
        # Left: Categories
        left_frame = tk.Frame(self.frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(left_frame, text="Categories").pack()
        self.category_listbox = tk.Listbox(left_frame, width=25, exportselection=False)
        self.category_listbox.pack(fill=tk.Y, expand=True)
        self.category_listbox.bind("<<ListboxSelect>>", self.on_category_select)

        cat_btn_frame = tk.Frame(left_frame)
        cat_btn_frame.pack(pady=5)
        tk.Button(cat_btn_frame, text="Add", command=self.add_category).pack(side=tk.LEFT)
        tk.Button(cat_btn_frame, text="Delete", command=self.delete_category).pack(side=tk.LEFT)
        tk.Button(cat_btn_frame, text="Rename", command=self.rename_category).pack(side=tk.LEFT)

        # Middle: Skills
        mid_frame = tk.Frame(self.frame)
        mid_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(mid_frame, text="Skills").pack()
        self.skills_listbox = tk.Listbox(mid_frame, width=30, exportselection=False)
        self.skills_listbox.pack(fill=tk.Y, expand=True)
        self.skills_listbox.bind("<<ListboxSelect>>", self.on_skill_select)

        skill_btn_frame = tk.Frame(mid_frame)
        skill_btn_frame.pack(pady=5)
        tk.Button(skill_btn_frame, text="Add", command=self.add_skill).pack(side=tk.LEFT)
        tk.Button(skill_btn_frame, text="Delete", command=self.delete_skill).pack(side=tk.LEFT)
        tk.Button(skill_btn_frame, text="Rename", command=self.rename_skill).pack(side=tk.LEFT)

        # Right: Aliases
        right_frame = tk.Frame(self.frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(right_frame, text="Aliases").pack()
        self.aliases_listbox = tk.Listbox(right_frame)
        self.aliases_listbox.pack(fill=tk.BOTH, expand=True)

        alias_btn_frame = tk.Frame(right_frame)
        alias_btn_frame.pack(pady=5)
        tk.Button(alias_btn_frame, text="Add", command=self.add_alias).pack(side=tk.LEFT)
        tk.Button(alias_btn_frame, text="Delete", command=self.delete_alias).pack(side=tk.LEFT)
        tk.Button(alias_btn_frame, text="Rename", command=self.rename_alias).pack(side=tk.LEFT)

    # === Category Methods ===
    def add_category(self):
        new_cat = simpledialog.askstring("Add Category", "Enter new category name:")
        if new_cat:
            new_cat = new_cat.strip()
            if new_cat in self.skills:
                messagebox.showerror("Error", "Category already exists.")
            else:
                self.skills[new_cat] = []
                self.refresh_categories()
                idx = list(sorted(self.skills.keys())).index(new_cat)
                self.category_listbox.selection_clear(0, tk.END)
                self.category_listbox.selection_set(idx)
                self.on_category_select()
                self.autosave()

    def delete_category(self):
        sel = self.category_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a category to delete.")
            return
        cat = self.category_listbox.get(sel[0])
        if messagebox.askyesno("Confirm", f"Delete category '{cat}' and all its skills?"):
            del self.skills[cat]
            self.refresh_categories()
            self.skills_listbox.delete(0, tk.END)
            self.aliases_listbox.delete(0, tk.END)
            self.autosave()

    def rename_category(self):
        sel = self.category_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a category to rename.")
            return
        old_cat = self.category_listbox.get(sel[0])
        new_cat = simpledialog.askstring("Rename Category", f"Rename '{old_cat}' to:")
        if new_cat:
            new_cat = new_cat.strip()
            if new_cat == old_cat:
                return
            if new_cat in self.skills:
                messagebox.showerror("Error", "Category already exists.")
                return
            self.skills[new_cat] = self.skills.pop(old_cat)
            self.refresh_categories()
            idx = list(sorted(self.skills.keys())).index(new_cat)
            self.category_listbox.selection_clear(0, tk.END)
            self.category_listbox.selection_set(idx)
            self.on_category_select()
            self.autosave()

    # === Skill Methods ===
    def add_skill(self):
        sel = self.category_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a category first.")
            return
        cat = self.category_listbox.get(sel[0])
        new_skill = simpledialog.askstring("Add Skill", f"Enter new skill for '{cat}':")
        if new_skill:
            new_skill = new_skill.strip()
            if any(s["name"] == new_skill for s in self.skills[cat]):
                messagebox.showerror("Error", "Skill already exists.")
            else:
                self.skills[cat].append({"name": new_skill, "aliases": []})
                self.refresh_skills(cat)
                self.autosave()

    def delete_skill(self):
        if self.last_selected_category is None or self.last_selected_skill_index is None:
            messagebox.showinfo("Info", "Select a skill to delete.")
            return
        cat = self.last_selected_category
        skill = self.skills[cat][self.last_selected_skill_index]["name"]
        if messagebox.askyesno("Confirm", f"Delete skill '{skill}' from '{cat}'?"):
            del self.skills[cat][self.last_selected_skill_index]
            self.refresh_skills(cat)
            self.aliases_listbox.delete(0, tk.END)
            self.last_selected_skill_index = None
            self.autosave()

    def rename_skill(self):
        if self.last_selected_category is None or self.last_selected_skill_index is None:
            messagebox.showinfo("Info", "Select a skill to rename.")
            return
        cat = self.last_selected_category
        old_skill = self.skills[cat][self.last_selected_skill_index]["name"]
        new_skill = simpledialog.askstring("Rename Skill", f"Enter new name for skill '{old_skill}':")
        if new_skill:
            new_skill = new_skill.strip()
            if new_skill == old_skill:
                return
            if any(s["name"] == new_skill for s in self.skills[cat]):
                messagebox.showerror("Error", "Skill already exists.")
                return
            self.skills[cat][self.last_selected_skill_index]["name"] = new_skill
            self.refresh_skills(cat)
            self.skills_listbox.selection_set(self.last_selected_skill_index)
            self.autosave()

    # === Alias Methods ===
    def add_alias(self):
        if self.last_selected_category is None or self.last_selected_skill_index is None:
            messagebox.showinfo("Info", "Select a skill first.")
            return
        cat = self.last_selected_category
        skill = self.skills[cat][self.last_selected_skill_index]
        new_alias = simpledialog.askstring("Add Alias", f"Enter alias for '{skill['name']}':")
        if new_alias:
            new_alias = new_alias.strip()
            if new_alias in skill["aliases"]:
                messagebox.showerror("Error", "Alias already exists.")
            else:
                skill["aliases"].append(new_alias)
                self.refresh_aliases(cat, self.last_selected_skill_index)
                self.autosave()

    def delete_alias(self):
        if self.last_selected_category is None or self.last_selected_skill_index is None:
            return
        alias_sel = self.aliases_listbox.curselection()
        if not alias_sel:
            messagebox.showinfo("Info", "Select an alias to delete.")
            return
        cat = self.last_selected_category
        skill = self.skills[cat][self.last_selected_skill_index]
        alias = self.aliases_listbox.get(alias_sel[0])
        if messagebox.askyesno("Confirm", f"Delete alias '{alias}'?"):
            skill["aliases"].remove(alias)
            self.refresh_aliases(cat, self.last_selected_skill_index)
            self.autosave()

    def rename_alias(self):
        if self.last_selected_category is None or self.last_selected_skill_index is None:
            return
        alias_sel = self.aliases_listbox.curselection()
        if not alias_sel:
            messagebox.showinfo("Info", "Select an alias to rename.")
            return
        cat = self.last_selected_category
        skill = self.skills[cat][self.last_selected_skill_index]
        old_alias = self.aliases_listbox.get(alias_sel[0])
        new_alias = simpledialog.askstring("Rename Alias", f"Rename alias '{old_alias}':")
        if new_alias:
            new_alias = new_alias.strip()
            if new_alias == old_alias:
                return
            if new_alias in skill["aliases"]:
                messagebox.showerror("Error", "Alias already exists.")
                return
            idx = skill["aliases"].index(old_alias)
            skill["aliases"][idx] = new_alias
            self.refresh_aliases(cat, self.last_selected_skill_index)
            self.autosave()

    # === Refresh + Event ===
    def refresh_categories(self):
        self.category_listbox.delete(0, tk.END)
        for cat in sorted(self.skills.keys()):
            self.category_listbox.insert(tk.END, cat)

    def refresh_skills(self, category):
        self.skills_listbox.delete(0, tk.END)
        for skill in self.skills.get(category, []):
            name = skill["name"] if isinstance(skill, dict) else skill
            self.skills_listbox.insert(tk.END, name)

    def refresh_aliases(self, category, skill_index):
        self.aliases_listbox.delete(0, tk.END)
        skill = self.skills[category][skill_index]
        for alias in sorted(skill.get("aliases", [])):
            self.aliases_listbox.insert(tk.END, alias)

    def on_category_select(self, event=None):
        sel = self.category_listbox.curselection()
        if not sel:
            return
        cat = self.category_listbox.get(sel[0])
        self.last_selected_category = cat
        self.last_selected_skill_index = None
        self.last_selected_skill = None
        self.refresh_skills(cat)
        self.aliases_listbox.delete(0, tk.END)

    def on_skill_select(self, event=None):
        sel = self.skills_listbox.curselection()
        if not sel:
            self.aliases_listbox.delete(0, tk.END)
            self.last_selected_skill_index = None
            self.last_selected_skill = None
            return
        idx = sel[0]
        cat = self.last_selected_category
        self.last_selected_skill_index = idx
        self.last_selected_skill = self.skills[cat][idx]["name"]
        self.refresh_aliases(cat, idx)

    def load_data(self, data):
        if not isinstance(data, dict):
            return
        normalized = {}
        for cat, skills in data.items():
            normalized[cat] = []
            if isinstance(skills, list):
                for skill in skills:
                    if isinstance(skill, dict) and "name" in skill:
                        normalized[cat].append(skill)
                    elif isinstance(skill, str):
                        normalized[cat].append({"name": skill, "aliases": []})
            elif isinstance(skills, dict):
                for skill_name, aliases in skills.items():
                    normalized[cat].append({"name": skill_name, "aliases": aliases if isinstance(aliases, list) else []})
        self.skills = normalized
        self.refresh_categories()
        self.skills_listbox.delete(0, tk.END)
        self.aliases_listbox.delete(0, tk.END)
        self.last_selected_category = None
        self.last_selected_skill_index = None
        self.last_selected_skill = None

    def autosave(self):
        try:
            if self.current_file:
                folder = os.path.dirname(self.current_file)
            else:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                project_dir = os.path.dirname(os.path.dirname(script_dir))
                folder = os.path.join(project_dir, "data")
                os.makedirs(folder, exist_ok=True)

            path = os.path.join(folder, "skills_autosave.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({
                    cat: [{"name": s["name"], "aliases": s.get("aliases", [])} for s in skills]
                    for cat, skills in self.skills.items()
                }, f, indent=2)
            print(f"Skills autosaved to {path}")
        except Exception as e:
            print(f"Skills autosave failed: {e}")
