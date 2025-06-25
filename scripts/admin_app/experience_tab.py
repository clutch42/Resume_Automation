import json
import tkinter as tk
from tkinter import ttk, messagebox
from base_tab import BaseTab
from utils import LargeEntryDialog

class ExperienceTab(BaseTab):
    def __init__(self, notebook):
        super().__init__(notebook, "Experience", "experience.json")
        self.experiences = []
        self.experience_drag_start_index = None
        self.dragged_experience_text = None
        self.detail_drag_start_index = None
        self.dragged_detail_text = None
        self.build_ui()

    def build_ui(self):
        # Left side: Experience list
        left_frame = tk.Frame(self.frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(left_frame, text="Experiences").pack()
        self.experience_listbox = tk.Listbox(left_frame, width=30)
        self.experience_listbox.pack(fill=tk.Y, expand=True)
        self.experience_listbox.config(exportselection=False)
        self.experience_listbox.bind("<<ListboxSelect>>", self.on_experience_select)
        self.experience_listbox.bind("<ButtonPress-1>", self.on_experience_drag_start)
        self.experience_listbox.bind("<B1-Motion>", self.on_experience_drag_motion)
        self.experience_listbox.bind("<ButtonRelease-1>", self.on_experience_drag_drop)

        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Experience", command=self.add_experience).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_experience).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Rename", command=self.rename_experience).pack(side=tk.LEFT, padx=5)

        # Right side
        right_frame = tk.Frame(self.frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top right: fields
        top_right_frame = tk.Frame(right_frame)
        top_right_frame.pack(fill=tk.X)

        labels = ["Title:", "Start Date:", "End Date:", "Location:"]
        self.entries = {}
        for i, label_text in enumerate(labels):
            label = tk.Label(top_right_frame, text=label_text)
            label.grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = tk.Entry(top_right_frame)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=2)
            entry.bind("<FocusOut>", self.on_field_change)
            self.entries[label_text[:-1].lower().replace(" ", "_")] = entry

        top_right_frame.columnconfigure(1, weight=1)

        # Bottom right: bullets
        bottom_right_frame = tk.Frame(right_frame)
        bottom_right_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        tk.Label(bottom_right_frame, text="Bullets").pack(anchor=tk.W)

        self.bullets_listbox = tk.Listbox(bottom_right_frame, height=8)
        self.bullets_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.bullets_listbox.bind("<<ListboxSelect>>", self.on_bullet_select)
        self.bullets_listbox.bind("<ButtonPress-1>", self.on_bullet_drag_start)
        self.bullets_listbox.bind("<B1-Motion>", self.on_bullet_drag_motion)
        self.bullets_listbox.bind("<ButtonRelease-1>", self.on_bullet_drag_drop)

        scrollbar = tk.Scrollbar(bottom_right_frame, command=self.bullets_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.bullets_listbox.config(yscrollcommand=scrollbar.set)

        tk.Label(bottom_right_frame, text="Bullet Content").pack(anchor=tk.W, pady=(10, 0))

        self.bullet_editor = tk.Text(bottom_right_frame, height=4, wrap=tk.WORD)
        self.bullet_editor.pack(fill=tk.X, expand=False)
        self.bullet_editor.bind("<FocusOut>", self.on_bullet_edit)

        bullets_btn_frame = tk.Frame(bottom_right_frame)
        bullets_btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        tk.Button(bullets_btn_frame, text="Add", command=self.add_bullet).pack(side=tk.LEFT, padx=5)
        tk.Button(bullets_btn_frame, text="Delete", command=self.delete_bullet).pack(side=tk.LEFT, padx=5)
        tk.Button(bullets_btn_frame, text="Modify", command=self.modify_bullet).pack(side=tk.LEFT, padx=5)

    # --- Experience Handlers ---

    def add_experience(self):
        dlg = LargeEntryDialog(self.frame, title="Add Experience", prompt="Enter employer name:")
        employer = dlg.result
        if employer:
            self.experiences.append({
                "title": "",
                "employer": employer,
                "start_date": "",
                "end_date": "",
                "location": "",
                "bullets": []
            })
            self.refresh_experience_list()
            self.experience_listbox.select_set(tk.END)
            self.on_experience_select()
            self.autosave()

    def delete_experience(self):
        index = self.get_selected_index()
        if index is None:
            messagebox.showwarning("Delete Experience", "No experience selected.")
            return
        if messagebox.askyesno("Delete Experience", "Are you sure you want to delete this experience?"):
            self.experiences.pop(index)
            self.refresh_experience_list()
            self.clear_fields()
            self.autosave()

    def rename_experience(self):
        index = self.get_selected_index()
        if index is None:
            messagebox.showwarning("Rename Experience", "No experience selected.")
            return
        current_employer = self.experiences[index]["employer"]
        dlg = LargeEntryDialog(self.frame, title="Rename Employer", prompt="Enter new employer name:", initialvalue=current_employer)
        new_name = dlg.result
        if new_name:
            self.experiences[index]["employer"] = new_name
            self.refresh_experience_list()
            self.experience_listbox.select_set(index)
            self.autosave()

    def on_experience_select(self, event=None):
        index = self.get_selected_index()
        if index is None:
            return
        self.current_index = index
        exp = self.experiences[index]
        for field in ["title", "start_date", "end_date", "location"]:
            value = exp.get(field, "")
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, value)
        self.refresh_bullets_list()
        self.bullet_editor.delete("1.0", tk.END)

    def get_selected_index(self):
        selection = self.experience_listbox.curselection()
        if not selection:
            return None
        return selection[0]

    def get_selected_experience(self):
        idx = self.get_selected_index()
        return None if idx is None else self.experiences[idx]

    def refresh_experience_list(self):
        self.experience_listbox.delete(0, tk.END)
        for exp in self.experiences:
            self.experience_listbox.insert(tk.END, exp["employer"])

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.bullets_listbox.delete(0, tk.END)
        self.bullet_editor.delete("1.0", tk.END)
        self.current_index = None

    def on_field_change(self, event):
        if self.current_index is None:
            return
        exp = self.experiences[self.current_index]
        for field, entry in self.entries.items():
            exp[field] = entry.get()
        self.autosave()

    def refresh_bullets_list(self):
        self.bullets_listbox.delete(0, tk.END)
        exp = self.get_selected_experience()
        if exp:
            for bullet in exp.get("bullets", []):
                self.bullets_listbox.insert(tk.END, bullet)

    def add_bullet(self):
        exp = self.get_selected_experience()
        if not exp:
            return
        dlg = LargeEntryDialog(self.frame, title="Add Bullet", prompt="Enter new bullet:", width=70, height=15)
        text = dlg.result
        if text:
            exp.setdefault("bullets", []).append(text)
            self.refresh_bullets_list()
            self.bullets_listbox.select_set(tk.END)
            self.on_bullet_select()
            self.autosave()

    def delete_bullet(self):
        exp = self.get_selected_experience()
        if not exp:
            return
        idxs = self.bullets_listbox.curselection()
        if not idxs:
            return
        idx = idxs[0]
        bullets = exp.get("bullets", [])
        if 0 <= idx < len(bullets):
            if messagebox.askyesno("Delete Bullet", "Are you sure you want to delete this bullet?"):
                bullets.pop(idx)
                self.refresh_bullets_list()
                self.bullet_editor.delete("1.0", tk.END)
                self.autosave()

    def modify_bullet(self):
        exp = self.get_selected_experience()
        if not exp:
            return
        idxs = self.bullets_listbox.curselection()
        if not idxs:
            return
        idx = idxs[0]
        bullets = exp.get("bullets", [])
        if 0 <= idx < len(bullets):
            dlg = LargeEntryDialog(self.frame, title="Modify Bullet", prompt="Edit bullet:", initialvalue=bullets[idx], width=70, height=15)
            new_text = dlg.result
            if new_text is not None:
                bullets[idx] = new_text
                self.refresh_bullets_list()
                self.bullets_listbox.select_set(idx)
                self.on_bullet_select()
                self.autosave()

    def on_bullet_select(self, event=None):
        exp = self.get_selected_experience()
        if not exp:
            return
        idxs = self.bullets_listbox.curselection()
        if not idxs:
            self.bullet_editor.delete("1.0", tk.END)
            return
        idx = idxs[0]
        bullets = exp.get("bullets", [])
        if 0 <= idx < len(bullets):
            self.bullet_editor.delete("1.0", tk.END)
            self.bullet_editor.insert(tk.END, bullets[idx])

    def on_bullet_edit(self, event=None):
        exp = self.get_selected_experience()
        if not exp:
            return
        idxs = self.bullets_listbox.curselection()
        if not idxs:
            return
        idx = idxs[0]
        bullets = exp.get("bullets", [])
        if 0 <= idx < len(bullets):
            new_text = self.bullet_editor.get("1.0", tk.END).strip()
            bullets[idx] = new_text
            self.refresh_bullets_list()
            self.bullets_listbox.select_set(idx)
            self.autosave()

    def on_experience_drag_start(self, event):
        self.experience_drag_start_index = self.experience_listbox.nearest(event.y)
        self.dragged_experience_text = self.experience_listbox.get(self.experience_drag_start_index)

    def on_experience_drag_motion(self, event):
        if self.experience_drag_start_index is None:
            return
        current_index = self.experience_listbox.nearest(event.y)
        if current_index != self.experience_drag_start_index:
            self.experiences[self.experience_drag_start_index], self.experiences[current_index] = self.experiences[current_index], self.experiences[self.experience_drag_start_index]
            self.refresh_experience_list()
            self.experience_listbox.selection_clear(0, tk.END)
            self.experience_listbox.selection_set(current_index)
            self.experience_drag_start_index = current_index

    def on_experience_drag_drop(self, event):
        if self.experience_drag_start_index is None:
            return
        self.autosave()
        self.experience_drag_start_index = None
        self.dragged_experience_text = None

    def on_bullet_drag_start(self, event):
        self.bullet_drag_start_index = self.bullets_listbox.nearest(event.y)
        self.dragged_bullet_text = self.bullets_listbox.get(self.bullet_drag_start_index)

    def on_bullet_drag_motion(self, event):
        if self.bullet_drag_start_index is None:
            return
        current_index = self.bullets_listbox.nearest(event.y)
        if current_index != self.bullet_drag_start_index:
            exp = self.get_selected_experience()
            if not exp:
                return
            bullets = exp.get("bullets", [])
            if current_index < 0 or current_index >= len(bullets):
                return
            bullets[self.bullet_drag_start_index], bullets[current_index] = bullets[current_index], bullets[self.bullet_drag_start_index]
            self.refresh_bullets_list()
            self.bullets_listbox.selection_clear(0, tk.END)
            self.bullets_listbox.selection_set(current_index)
            self.bullet_drag_start_index = current_index

    def on_bullet_drag_drop(self, event):
        if self.bullet_drag_start_index is None:
            return
        self.autosave()
        self.bullet_drag_start_index = None
        self.dragged_bullet_text = None

    def get_data(self):
        return self.experiences

    def load_data(self, data):
        self.experiences = []
        for item in data:
            if isinstance(item, dict) and "employer" in item:
                self.experiences.append({
                    "title": item.get("title", ""),
                    "employer": item["employer"],
                    "start_date": item.get("start_date", ""),
                    "end_date": item.get("end_date", ""),
                    "location": item.get("location", ""),
                    "bullets": item.get("bullets", [])
                })
        self.refresh_experience_list()
        self.clear_fields()
