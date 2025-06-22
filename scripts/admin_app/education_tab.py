import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class EducationTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook)
        notebook.add(self.frame, text="Education")

        self.degrees = []
        self.current_degree_index = None
        self.current_file = None

        self.build_ui()

    def build_ui(self):
        # Left side: Degree list
        left_frame = tk.Frame(self.frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(left_frame, text="Degrees").pack()
        self.degree_listbox = tk.Listbox(left_frame, width=30, exportselection=False)
        self.degree_listbox.pack(fill=tk.Y, expand=True)
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

        self.details_text = tk.Text(bottom_right_frame, height=10, wrap=tk.WORD)
        self.details_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(bottom_right_frame, command=self.details_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_text.config(yscrollcommand=scrollbar.set)

        self.details_text.bind("<Button-1>", self.select_detail_line)

        # Buttons for details
        details_btn_frame = tk.Frame(bottom_right_frame)
        details_btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        tk.Button(details_btn_frame, text="Add Detail", command=self.add_detail).pack(side=tk.LEFT, padx=5)
        tk.Button(details_btn_frame, text="Delete Detail", command=self.delete_detail).pack(side=tk.LEFT, padx=5)
        tk.Button(details_btn_frame, text="Modify Detail", command=self.modify_detail).pack(side=tk.LEFT, padx=5)

    # --- Degree List Handlers ---

    def add_degree(self):
        new_degree_name = simpledialog.askstring("Add Degree", "Enter new degree name:")
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
        new_name = simpledialog.askstring("Rename Degree", "Enter new degree name:", initialvalue=current_name)
        if new_name:
            self.degrees[index]["degree"] = new_name
            self.refresh_degree_list()
            self.degree_listbox.select_set(index)
            self.autosave()

    def on_degree_select(self, event=None):
        index = self.get_selected_degree_index()
        if index is None:
            self.clear_fields()
            return
        self.current_degree_index = index
        degree = self.degrees[index]

        # Load top right fields
        for field in ["school", "gpa", "start_date", "end_date", "location"]:
            value = degree.get(field) or ""
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, value)

        # Load details
        self.refresh_details_text()

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
        self.details_text.delete("1.0", tk.END)
        self.current_degree_index = None

    def on_field_change(self, event):
        if self.current_degree_index is None:
            return
        degree = self.degrees[self.current_degree_index]
        for field, entry in self.entries.items():
            degree[field] = entry.get()
        self.autosave()

    # --- Details Handlers ---
    def select_detail_line(self, event):
        # Get index of click position
        index = self.details_text.index(f"@{event.x},{event.y}")
        line_number = index.split('.')[0]

        # Select whole line
        line_start = f"{line_number}.0"
        line_end = f"{line_number}.end"

        self.details_text.tag_remove(tk.SEL, "1.0", tk.END)
        self.details_text.tag_add(tk.SEL, line_start, line_end)

        # Move cursor to start of line (optional, but helps UX)
        self.details_text.mark_set(tk.INSERT, line_start)

        # Prevent default cursor placement (optional)
        return "break"


    def get_selected_detail_index(self):
        try:
            # Get current cursor line (1-based)
            index = self.details_text.index(tk.INSERT).split('.')[0]
            return int(index) - 1
        except Exception:
            return None

    def refresh_details_text(self):
        self.details_text.delete("1.0", tk.END)
        degree = self.get_selected_degree()
        if degree:
            for detail in degree.get("details", []):
                self.details_text.insert(tk.END, detail + "\n")

    def add_detail(self):
        degree = self.get_selected_degree()
        if not degree:
            messagebox.showwarning("Add Detail", "No degree selected.")
            return
        new_detail = simpledialog.askstring("Add Detail", "Enter new detail:")
        if new_detail:
            degree.setdefault("details", []).append(new_detail)
            self.refresh_details_text()
            self.autosave()

    def delete_detail(self):
        degree = self.get_selected_degree()
        if not degree:
            messagebox.showwarning("Delete Detail", "No degree selected.")
            return
        idx = self.get_selected_detail_index()
        if idx is None:
            messagebox.showwarning("Delete Detail", "Place cursor on the detail line to delete.")
            return
        details = degree.get("details", [])
        if 0 <= idx < len(details):
            details.pop(idx)
            self.refresh_details_text()
            self.autosave()

    def modify_detail(self):
        degree = self.get_selected_degree()
        if not degree:
            messagebox.showwarning("Modify Detail", "No degree selected.")
            return
        idx = self.get_selected_detail_index()
        if idx is None:
            messagebox.showwarning("Modify Detail", "Place cursor on the detail line to modify.")
            return
        details = degree.get("details", [])
        if 0 <= idx < len(details):
            current_detail = details[idx]
            new_detail = simpledialog.askstring("Modify Detail", "Edit detail:", initialvalue=current_detail)
            if new_detail is not None:
                details[idx] = new_detail
                self.refresh_details_text()
                self.autosave()

    def load_data(self, data):
        if not isinstance(data, list):
            return
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
        self.current_degree_index = None

    def save_to_file(self, filepath=None):
        if filepath:
            self.current_file = filepath
        if not self.current_file:
            return
        try:
            with open(self.current_file, "w", encoding="utf-8") as f:
                json.dump(self.degrees, f, indent=2)
            print(f"Education data saved to {self.current_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save education data:\n{e}")

    def autosave(self):
        try:
            if self.current_file:
                folder = os.path.dirname(self.current_file)
            else:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                project_dir = os.path.dirname(os.path.dirname(script_dir))
                folder = os.path.join(project_dir, "data")
                os.makedirs(folder, exist_ok=True)

            path = os.path.join(folder, "education_autosave.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.degrees, f, indent=2)
            print(f"Education autosaved to {path}")
        except Exception as e:
            print(f"Education autosave failed: {e}")
