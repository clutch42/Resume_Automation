import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from base_tab import BaseTab
from utils import LargeEntryDialog

class EducationTab(BaseTab):
    def __init__(self, notebook):
        super().__init__(notebook, "Education", "education.json")
        self.degrees = []
        self.build_ui()

    def build_ui(self):
        # Left side: Degree list
        left_frame = tk.Frame(self.frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(left_frame, text="Degrees").pack()
        self.degree_listbox = tk.Listbox(left_frame, width=30)
        self.degree_listbox.pack(fill=tk.Y, expand=True)
        self.degree_listbox.config(exportselection=False)
        self.degree_listbox.bind("<<ListboxSelect>>", self.on_degree_select)

        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Degree", command=self.add_degree).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Degree", command=self.delete_degree).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Rename Degree", command=self.rename_degree).pack(side=tk.LEFT, padx=5)

        # Right side: Top and bottom frames
        right_frame = tk.Frame(self.frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top right: fields
        top_right_frame = tk.Frame(right_frame)
        top_right_frame.pack(fill=tk.X)

        labels = ["School:", "GPA:", "Start Date:", "End Date:", "Location:"]
        self.entries = {}
        for i, label_text in enumerate(labels):
            label = tk.Label(top_right_frame, text=label_text)
            label.grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = tk.Entry(top_right_frame)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=2)
            entry.bind("<FocusOut>", self.on_field_change)
            self.entries[label_text[:-1].lower().replace(" ", "_")] = entry

        top_right_frame.columnconfigure(1, weight=1)

        # Bottom right: details list (scrollable)
        bottom_right_frame = tk.Frame(right_frame)
        bottom_right_frame.pack(fill=tk.BOTH, expand=True, pady=(10,0))

        tk.Label(bottom_right_frame, text="Details").pack(anchor=tk.W)

        # Listbox to show list of details
        self.details_listbox = tk.Listbox(bottom_right_frame, height=8)
        self.details_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.details_listbox.bind("<<ListboxSelect>>", self.on_detail_select)

        # Scrollbar for the Listbox
        scrollbar = tk.Scrollbar(bottom_right_frame, command=self.details_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_listbox.config(yscrollcommand=scrollbar.set)

        # Editable text area for selected detail
        tk.Label(bottom_right_frame, text="Detail Content").pack(anchor=tk.W, pady=(10, 0))

        self.detail_editor = tk.Text(bottom_right_frame, height=4, wrap=tk.WORD)
        self.detail_editor.pack(fill=tk.X, expand=False)
        self.detail_editor.bind("<FocusOut>", self.on_detail_edit)

        # Buttons for details
        details_btn_frame = tk.Frame(bottom_right_frame)
        details_btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        tk.Button(details_btn_frame, text="Add Detail", command=self.add_detail).pack(side=tk.LEFT, padx=5)
        tk.Button(details_btn_frame, text="Delete Detail", command=self.delete_detail).pack(side=tk.LEFT, padx=5)
        tk.Button(details_btn_frame, text="Modify Detail", command=self.modify_detail).pack(side=tk.LEFT, padx=5)

    # --- Degree List Handlers ---

    def add_degree(self):
        dlg = LargeEntryDialog(self.frame, title="Add Degree", prompt="Enter new degree name:")
        new_degree_name = dlg.result
        if new_degree_name:
            self.degrees.append({
                "degree": new_degree_name,
                "school": "",
                "gpa": "",
                "start_date": "",
                "end_date": "",
                "location": "",
                "details": []
            })
            self.refresh_degree_list()
            self.degree_listbox.select_set(tk.END)
            self.on_degree_select()
            self.autosave()

    def delete_degree(self):
        index = self.get_selected_degree_index()
        if index is None:
            messagebox.showwarning("Delete Degree", "No degree selected.")
            return
        if messagebox.askyesno("Delete Degree", "Are you sure you want to delete this degree?"):
            self.degrees.pop(index)
            self.refresh_degree_list()
            self.clear_fields()
            self.autosave()

    def rename_degree(self):
        index = self.get_selected_degree_index()
        if index is None:
            messagebox.showwarning("Rename Degree", "No degree selected.")
            return
        current_name = self.degrees[index]["degree"]
        dlg = LargeEntryDialog(self.frame, title="Rename Degree", prompt="Enter new degree name:", initialvalue=current_name)
        new_name = dlg.result
        if new_name:
            self.degrees[index]["degree"] = new_name
            self.refresh_degree_list()
            self.degree_listbox.select_set(index)
            self.autosave()

    def on_degree_select(self, event=None):
        index = self.get_selected_degree_index()
        if index is None:
            return
        self.current_degree_index = index
        degree = self.degrees[index]

        # Load top right fields
        for field in ["school", "gpa", "start_date", "end_date", "location"]:
            value = degree.get(field) or ""
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, value)

        # Load details
        self.refresh_details_list()

    def get_selected_degree_index(self):
        selection = self.degree_listbox.curselection()
        if not selection:
            return None
        return selection[0]

    def get_selected_degree(self):
        index = self.get_selected_degree_index()
        if index is None:
            return None
        return self.degrees[index]

    def refresh_degree_list(self):
        self.degree_listbox.delete(0, tk.END)
        for degree in self.degrees:
            self.degree_listbox.insert(tk.END, degree["degree"])

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.details_listbox.delete(0, tk.END)
        self.detail_editor.delete("1.0", tk.END)
        self.current_degree_index = None

    def on_field_change(self, event):
        if self.current_degree_index is None:
            return
        degree = self.degrees[self.current_degree_index]
        for field, entry in self.entries.items():
            degree[field] = entry.get()
        self.autosave()

    def refresh_details_list(self):
        self.details_listbox.delete(0, tk.END)
        degree = self.get_selected_degree()
        if degree:
            for detail in degree.get("details", []):
                self.details_listbox.insert(tk.END, detail)

    def add_detail(self):
        degree = self.get_selected_degree()
        if not degree:
            messagebox.showwarning("Add Detail", "No degree selected.")
            return
        dlg = LargeEntryDialog(self.frame, title="Add Detail", prompt="Enter new detail:", width=70, height=15)
        new_detail = dlg.result
        if new_detail:
            degree.setdefault("details", []).append(new_detail)
            self.refresh_details_list()
            self.details_listbox.select_set(tk.END)
            self.on_detail_select()
            self.autosave()

    def delete_detail(self):
        degree = self.get_selected_degree()
        if not degree:
            messagebox.showwarning("Delete Detail", "No degree selected.")
            return
        idxs = self.details_listbox.curselection()
        if not idxs:
            messagebox.showwarning("Delete Detail", "No detail selected.")
            return
        idx = idxs[0]
        details = degree.get("details", [])
        if 0 <= idx < len(details):
            if messagebox.askyesno("Delete Detail", "Are you sure you want to delete this detail?"):
                details.pop(idx)
                self.refresh_details_list()
                self.detail_editor.delete("1.0", tk.END)
                self.autosave()

    def modify_detail(self):
        degree = self.get_selected_degree()
        if not degree:
            messagebox.showwarning("Modify Detail", "No degree selected.")
            return
        idxs = self.details_listbox.curselection()
        if not idxs:
            messagebox.showwarning("Modify Detail", "No detail selected.")
            return
        idx = idxs[0]
        details = degree.get("details", [])
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
        degree = self.get_selected_degree()
        if not degree:
            return
        idxs = self.details_listbox.curselection()
        if not idxs:
            self.detail_editor.delete("1.0", tk.END)
            return
        idx = idxs[0]
        details = degree.get("details", [])
        if 0 <= idx < len(details):
            self.detail_editor.delete("1.0", tk.END)
            self.detail_editor.insert(tk.END, details[idx])

    def on_detail_edit(self, event=None):
        degree = self.get_selected_degree()
        if not degree:
            return
        idxs = self.details_listbox.curselection()
        if not idxs:
            return
        idx = idxs[0]
        details = degree.get("details", [])
        if 0 <= idx < len(details):
            new_text = self.detail_editor.get("1.0", tk.END).strip()
            details[idx] = new_text
            self.refresh_details_list()
            self.details_listbox.select_set(idx)
            self.autosave()

    def get_data(self):
        return self.degrees

    def load_data(self, data):
        self.degrees = []
        for item in data:
            if isinstance(item, dict) and "degree" in item:
                self.degrees.append({
                    "degree": item["degree"],
                    "school": item.get("school", ""),
                    "gpa": item.get("gpa", ""),
                    "start_date": item.get("start_date", ""),
                    "end_date": item.get("end_date", ""),
                    "location": item.get("location", ""),
                    "details": item.get("details", [])
                })
        self.refresh_degree_list()
        self.clear_fields()
