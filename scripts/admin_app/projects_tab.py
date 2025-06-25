import json
import tkinter as tk
from tkinter import ttk, messagebox
from base_tab import BaseTab
from utils import LargeEntryDialog

class ProjectsTab(BaseTab):
    def __init__(self, notebook):
        super().__init__(notebook, "Projects", "projects.json")
        self.projects_page_url = ""
        self.projects = []
        self.project_drag_start_index = None
        self.dragged_project_text = None
        self.detail_drag_start_index = None
        self.dragged_detail_text = None
        self.current_project_index = None
        self.build_ui()

    def build_ui(self):
        # Top: Projects Page URL
        top_frame = tk.Frame(self.frame)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(top_frame, text="Projects Page URL:").pack(side=tk.LEFT)
        self.url_entry = tk.Entry(top_frame)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.url_entry.bind("<FocusOut>", self.on_url_change)

        # Main frame split left/right
        main_frame = tk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Project list
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(left_frame, text="Projects").pack()
        self.project_listbox = tk.Listbox(left_frame, width=30)
        self.project_listbox.pack(fill=tk.Y, expand=True)
        self.project_listbox.config(exportselection=False)
        self.project_listbox.bind("<<ListboxSelect>>", self.on_project_select)
        self.project_listbox.bind("<ButtonPress-1>", self.on_project_drag_start)
        self.project_listbox.bind("<B1-Motion>", self.on_project_drag_motion)
        self.project_listbox.bind("<ButtonRelease-1>", self.on_project_drag_drop)

        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Project", command=self.add_project).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Project", command=self.delete_project).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Rename Project", command=self.rename_project).pack(side=tk.LEFT, padx=5)

        # Right: Project details
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Name and URL fields
        fields_frame = tk.Frame(right_frame)
        fields_frame.pack(fill=tk.X)

        tk.Label(fields_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = tk.Entry(fields_frame)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, pady=2)
        self.name_entry.bind("<FocusOut>", self.on_field_change)

        tk.Label(fields_frame, text="URL:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.url_field_entry = tk.Entry(fields_frame)
        self.url_field_entry.grid(row=1, column=1, sticky=tk.EW, pady=2)
        self.url_field_entry.bind("<FocusOut>", self.on_field_change)

        fields_frame.columnconfigure(1, weight=1)

        # Details list and editor
        details_frame = tk.Frame(right_frame)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        tk.Label(details_frame, text="Details").pack(anchor=tk.W)
        self.details_listbox = tk.Listbox(details_frame, height=8)
        self.details_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.details_listbox.bind("<<ListboxSelect>>", self.on_detail_select)
        self.details_listbox.bind("<ButtonPress-1>", self.on_detail_drag_start)
        self.details_listbox.bind("<B1-Motion>", self.on_detail_drag_motion)
        self.details_listbox.bind("<ButtonRelease-1>", self.on_detail_drag_drop)

        scrollbar = tk.Scrollbar(details_frame, command=self.details_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_listbox.config(yscrollcommand=scrollbar.set)

        tk.Label(details_frame, text="Detail Content").pack(anchor=tk.W, pady=(10, 0))
        self.detail_editor = tk.Text(details_frame, height=4, wrap=tk.WORD)
        self.detail_editor.pack(fill=tk.X, expand=False)
        self.detail_editor.bind("<FocusOut>", self.on_detail_edit)

        btns_frame = tk.Frame(details_frame)
        btns_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        tk.Button(btns_frame, text="Add Detail", command=self.add_detail).pack(side=tk.LEFT, padx=5)
        tk.Button(btns_frame, text="Delete Detail", command=self.delete_detail).pack(side=tk.LEFT, padx=5)
        tk.Button(btns_frame, text="Modify Detail", command=self.modify_detail).pack(side=tk.LEFT, padx=5)

    # URL field handler
    def on_url_change(self, event=None):
        new_url = self.url_entry.get().strip()
        if new_url != self.projects_page_url:
            self.projects_page_url = new_url
            self.autosave()

    # --- Project List Handlers ---

    def add_project(self):
        dlg = LargeEntryDialog(self.frame, title="Add Project", prompt="Enter new project name:")
        new_name = dlg.result
        if new_name:
            self.projects.append({
                "name": new_name,
                "url": None,
                "details": []
            })
            self.refresh_project_list()
            self.project_listbox.select_set(tk.END)
            self.on_project_select()
            self.autosave()

    def delete_project(self):
        idx = self.get_selected_project_index()
        if idx is None:
            messagebox.showwarning("Delete Project", "No project selected.")
            return
        if messagebox.askyesno("Delete Project", "Are you sure you want to delete this project?"):
            self.projects.pop(idx)
            self.refresh_project_list()
            self.clear_fields()
            self.autosave()

    def rename_project(self):
        idx = self.get_selected_project_index()
        if idx is None:
            messagebox.showwarning("Rename Project", "No project selected.")
            return
        current_name = self.projects[idx]["name"]
        dlg = LargeEntryDialog(self.frame, title="Rename Project", prompt="Enter new project name:", initialvalue=current_name)
        new_name = dlg.result
        if new_name:
            self.projects[idx]["name"] = new_name
            self.refresh_project_list()
            self.project_listbox.select_set(idx)
            self.autosave()

    def on_project_select(self, event=None):
        idx = self.get_selected_project_index()
        if idx is None:
            return
        self.current_project_index = idx
        project = self.projects[idx]

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, project.get("name", ""))

        self.url_field_entry.delete(0, tk.END)
        if project.get("url"):
            self.url_field_entry.insert(0, project["url"])

        self.refresh_details_list()
        self.detail_editor.delete("1.0", tk.END)

    def get_selected_project_index(self):
        selection = self.project_listbox.curselection()
        if not selection:
            return None
        return selection[0]

    def refresh_project_list(self):
        self.project_listbox.delete(0, tk.END)
        for proj in self.projects:
            self.project_listbox.insert(tk.END, proj.get("name", "Unnamed Project"))

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.url_field_entry.delete(0, tk.END)
        self.details_listbox.delete(0, tk.END)
        self.detail_editor.delete("1.0", tk.END)
        self.current_project_index = None

    def on_field_change(self, event=None):
        if self.current_project_index is None:
            return
        project = self.projects[self.current_project_index]
        project["name"] = self.name_entry.get()
        url_text = self.url_field_entry.get().strip()
        project["url"] = url_text if url_text else None
        self.refresh_project_list()
        self.project_listbox.select_set(self.current_project_index)
        self.autosave()

    # --- Details List Handlers ---

    def refresh_details_list(self):
        self.details_listbox.delete(0, tk.END)
        project = self.get_selected_project()
        if project:
            for detail in project.get("details", []):
                self.details_listbox.insert(tk.END, detail)

    def get_selected_project(self):
        if self.current_project_index is None:
            return None
        return self.projects[self.current_project_index]

    def add_detail(self):
        project = self.get_selected_project()
        if not project:
            messagebox.showwarning("Add Detail", "No project selected.")
            return
        dlg = LargeEntryDialog(self.frame, title="Add Detail", prompt="Enter new detail:", width=70, height=15)
        new_detail = dlg.result
        if new_detail:
            project.setdefault("details", []).append(new_detail)
            self.refresh_details_list()
            self.details_listbox.select_set(tk.END)
            self.on_detail_select()
            self.autosave()

    def delete_detail(self):
        project = self.get_selected_project()
        if not project:
            messagebox.showwarning("Delete Detail", "No project selected.")
            return
        idxs = self.details_listbox.curselection()
        if not idxs:
            messagebox.showwarning("Delete Detail", "No detail selected.")
            return
        idx = idxs[0]
        details = project.get("details", [])
        if 0 <= idx < len(details):
            if messagebox.askyesno("Delete Detail", "Are you sure you want to delete this detail?"):
                details.pop(idx)
                self.refresh_details_list()
                self.detail_editor.delete("1.0", tk.END)
                self.autosave()

    def modify_detail(self):
        project = self.get_selected_project()
        if not project:
            messagebox.showwarning("Modify Detail", "No project selected.")
            return
        idxs = self.details_listbox.curselection()
        if not idxs:
            messagebox.showwarning("Modify Detail", "No detail selected.")
            return
        idx = idxs[0]
        details = project.get("details", [])
        if 0 <= idx < len(details):
            current_detail = details[idx]
            dlg = LargeEntryDialog(self.frame, title="Modify Detail", prompt="Edit detail:", initialvalue=current_detail, width=70, height=15)
            new_detail = dlg.result
            if new_detail is not None:
                details[idx] = new_detail
                self.refresh_details_list()
                self.details_listbox.select_set(idx)
                self.on_detail_select()
                self.autosave()

    def on_detail_select(self, event=None):
        project = self.get_selected_project()
        if not project:
            return
        idxs = self.details_listbox.curselection()
        if not idxs:
            self.detail_editor.delete("1.0", tk.END)
            return
        idx = idxs[0]
        details = project.get("details", [])
        if 0 <= idx < len(details):
            self.detail_editor.delete("1.0", tk.END)
            self.detail_editor.insert("1.0", details[idx])

    def on_detail_edit(self, event=None):
        project = self.get_selected_project()
        if not project:
            return
        idxs = self.details_listbox.curselection()
        if not idxs:
            return
        idx = idxs[0]
        new_text = self.detail_editor.get("1.0", tk.END).strip()
        details = project.get("details", [])
        if 0 <= idx < len(details) and new_text != details[idx]:
            details[idx] = new_text
            self.refresh_details_list()
            self.details_listbox.select_set(idx)
            self.autosave()

    def on_project_drag_start(self, event):
        self.project_drag_start_index = self.project_listbox.nearest(event.y)
        self.dragged_project_text = self.project_listbox.get(self.project_drag_start_index)

    def on_project_drag_motion(self, event):
        if self.project_drag_start_index is None:
            return
        current_index = self.project_listbox.nearest(event.y)
        if current_index != self.project_drag_start_index:
            # Swap projects in the data list
            self.projects[self.project_drag_start_index], self.projects[current_index] = (
                self.projects[current_index], self.projects[self.project_drag_start_index]
            )
            self.refresh_project_list()
            self.project_listbox.selection_clear(0, tk.END)
            self.project_listbox.selection_set(current_index)
            self.project_drag_start_index = current_index

    def on_project_drag_drop(self, event):
        if self.project_drag_start_index is None:
            return
        self.autosave()
        self.project_drag_start_index = None
        self.dragged_project_text = None

    def on_detail_drag_start(self, event):
        self.detail_drag_start_index = self.details_listbox.nearest(event.y)
        self.dragged_detail_text = self.details_listbox.get(self.detail_drag_start_index)

    def on_detail_drag_motion(self, event):
        if self.detail_drag_start_index is None:
            return
        current_index = self.details_listbox.nearest(event.y)
        if current_index != self.detail_drag_start_index:
            project = self.get_selected_project()
            if not project:
                return
            details = project.get("details", [])
            if current_index < 0 or current_index >= len(details):
                return
            # Swap details in the current project's details list
            details[self.detail_drag_start_index], details[current_index] = (
                details[current_index], details[self.detail_drag_start_index]
            )
            self.refresh_details_list()
            self.details_listbox.selection_clear(0, tk.END)
            self.details_listbox.selection_set(current_index)
            self.detail_drag_start_index = current_index

    def on_detail_drag_drop(self, event):
        if self.detail_drag_start_index is None:
            return
        self.autosave()
        self.detail_drag_start_index = None
        self.dragged_detail_text = None


    # --- Load/Save ---

    def load_data(self, data):
        self.projects_page_url = data.get("projects_page_url", "")
        self.projects = data.get("projects", [])
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, self.projects_page_url)
        self.refresh_project_list()
        self.clear_fields()

    def get_data(self):
        return {
            "projects_page_url": self.projects_page_url,
            "projects": self.projects
        }
    