import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from base_tab import BaseTab  # adjust as needed

class SummariesTab(BaseTab):
    def __init__(self, notebook):
        super().__init__(notebook, "Summaries", "summaries.json")
        self.summaries = {}
        self.current_key = None
        self.current_file_path = None
        self.build_ui()

    def build_ui(self):
        top = ttk.Frame(self.frame)
        top.pack(fill="x", padx=10, pady=5)

        ttk.Label(top, text="Summary:").pack(side="left")
        self.summary_var = tk.StringVar()
        self.dropdown = ttk.Combobox(top, textvariable=self.summary_var, state="readonly")
        self.dropdown.pack(side="left", padx=5)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_select)

        ttk.Button(top, text="Add", command=self.add_summary).pack(side="left", padx=5)
        ttk.Button(top, text="Delete", command=self.delete_summary).pack(side="left", padx=5)
        ttk.Button(top, text="Save", command=self.save_summary).pack(side="left", padx=5)

        self.text = tk.Text(self.frame, wrap="word")
        self.text.pack(fill="both", expand=True, padx=10, pady=5)

    def load_data(self, data):
        self.summaries = data
        self.dropdown["values"] = list(self.summaries.keys())
        self.current_key = None
        self.current_file_path = None
        self.summary_var.set("")
        self.text.delete("1.0", tk.END)

    def on_select(self, event=None):
        key = self.summary_var.get()
        if key and key in self.summaries:
            path = os.path.join(os.path.dirname(self.current_file), self.summaries[key])
            self.current_key = key
            self.current_file_path = path
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.text.delete("1.0", tk.END)
                    self.text.insert(tk.END, f.read())
            except Exception as e:
                messagebox.showerror("Error", f"Could not read summary:\n{e}")

    def add_summary(self):
        name = simpledialog.askstring("New Summary", "Enter summary label (e.g., 'Data Analyst'):")
        if not name:
            return
        name = name.strip()
        if not name or name in self.summaries:
            messagebox.showerror("Error", "Invalid or duplicate summary name.")
            return

        filename = name.lower().replace(" ", "_") + ".txt"
        rel_path = os.path.join("summaries", filename)
        abs_path = os.path.join(os.path.dirname(self.current_file), rel_path)

        try:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write("")
            self.summaries[name] = rel_path.replace("\\", "/")
            self.dropdown["values"] = list(self.summaries.keys())
            self.summary_var.set(name)
            self.on_select()
            self.autosave()
        except Exception as e:
            messagebox.showerror("Error", f"Could not create summary:\n{e}")

    def delete_summary(self):
        key = self.summary_var.get()
        if not key:
            return
        # Prevent deleting the default summary
        if key == "default":
            messagebox.showerror("Error", "The default summary cannot be deleted.")
            return
        if messagebox.askyesno("Delete", f"Delete summary '{key}'?"):
            try:
                os.remove(os.path.join(os.path.dirname(self.current_file), self.summaries[key]))
            except FileNotFoundError:
                pass
            del self.summaries[key]
            self.dropdown["values"] = list(self.summaries.keys())
            self.text.delete("1.0", tk.END)
            self.summary_var.set("")
            self.current_key = None
            self.current_file_path = None
            self.save()

    def save_summary(self):
        if not self.current_file_path:
            return
        try:
            content = self.text.get("1.0", tk.END).strip()
            with open(self.current_file_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Summary '{self.current_key}' saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save summary:\n{e}")

    def get_data(self):
        return self.summaries
