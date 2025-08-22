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
        self.skills_vars = {}
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

        # Summary Text Area
        ttk.Label(self.frame, text="Summary Text:").pack(anchor="w", padx=10, pady=(10, 0))
        self.text = tk.Text(self.frame, wrap="word", height=10)
        self.text.pack(fill="both", expand=True, padx=10)

        # Cover Letter Text Area
        ttk.Label(self.frame, text="Cover Letter Text:").pack(anchor="w", padx=10, pady=(10, 0))
        self.cover_letter_text = tk.Text(self.frame, wrap="word", height=12)
        self.cover_letter_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # In build_ui of SummariesTab
        self.skills_frame = tk.Frame(self.frame)
        self.skills_frame.pack(fill="x", pady=10)

    def build_skills_categories_checkboxes(self, skills_data):
        # Clear previous checkboxes if any
        for widget in self.skills_frame.winfo_children():
            widget.destroy()
        
        self.skills_vars = {}  # reset dictionary

        for category in skills_data.keys():
            var = tk.BooleanVar()
            self.skills_vars[category] = var
            cb = tk.Checkbutton(self.skills_frame, text=category, variable=var)
            cb.pack(anchor="w", pady=2)

    def load_data(self, data):
        self.summaries = data
        self.dropdown["values"] = list(self.summaries.keys())

        # Set current key and file
        self.current_key = "default"
        self.current_file = os.path.join(self.user_folder_path, "summaries.json")  # ensure on_select has a valid file
        self.current_file_path = self.summaries[self.current_key]

        # Set dropdown to default
        self.summary_var.set("default")

        # Clear text areas first
        self.text.delete("1.0", tk.END)
        if hasattr(self, "cover_letter_text"):
            self.cover_letter_text.delete("1.0", tk.END)

        # Load the summary and cover letter
        self.on_select()

        # Load skills categories
        skills_path = os.path.join(self.user_folder_path, "skills.json")
        with open(skills_path, "r", encoding="utf-8") as f:
            skills_data = json.load(f)
        self.build_skills_categories_checkboxes(skills_data)

    def on_select(self, event=None):
        if not self.current_file:
            print("[DEBUG] on_select skipped — no file loaded yet")
            return
        key = self.summary_var.get()
        if key and key in self.summaries:
            base_path = os.path.dirname(self.current_file)
            paths = self.summaries[key]

            # Load summary
            summary_path = os.path.join(base_path, paths.get("summary", ""))
            self.current_key = key
            self.current_file_path = summary_path
            try:
                with open(summary_path, "r", encoding="utf-8") as f:
                    self.text.delete("1.0", tk.END)
                    self.text.insert(tk.END, f.read())
            except Exception as e:
                messagebox.showerror("Error", f"Could not read summary:\n{e}")
                self.text.delete("1.0", tk.END)

            # Load cover letter
            cover_path = os.path.join(base_path, paths.get("cover_letter", ""))
            try:
                with open(cover_path, "r", encoding="utf-8") as f:
                    self.cover_letter_text.delete("1.0", tk.END)
                    self.cover_letter_text.insert(tk.END, f.read())
            except Exception:
                # It's valid to have no cover letter — just clear the field
                self.cover_letter_text.delete("1.0", tk.END)

    def add_summary(self):
        name = simpledialog.askstring("New Entry", "Enter label (e.g., 'Data Analyst'):")
        if not name:
            return

        name = name.strip()
        if not name or name in self.summaries:
            messagebox.showerror("Error", "Invalid or duplicate name.")
            return

        base_dir = os.path.dirname(self.current_file)
        file_base = name.lower().replace(" ", "_")
        summaries_dir = os.path.join(base_dir, "summaries")

        summary_rel_path = os.path.join("summaries", f"{file_base}.txt")
        cover_rel_path = os.path.join("cover_letters", f"{file_base}_cover.txt")
        summary_abs_path = os.path.join(base_dir, summary_rel_path)
        cover_abs_path = os.path.join(base_dir, cover_rel_path)

        try:
            os.makedirs(summaries_dir, exist_ok=True)

            with open(summary_abs_path, "w", encoding="utf-8") as f:
                f.write("")

            with open(cover_abs_path, "w", encoding="utf-8") as f:
                f.write("")

            self.summaries[name] = {
                "summary": summary_rel_path.replace("\\", "/"),
                "cover_letter": cover_rel_path.replace("\\", "/")
            }

            self.dropdown["values"] = list(self.summaries.keys())
            self.summary_var.set(name)
            self.on_select()
            self.save()
        except Exception as e:
            messagebox.showerror("Error", f"Could not create files:\n{e}")

    def delete_summary(self):
        key = self.summary_var.get()
        if not key:
            return
        if key == "default":
            messagebox.showerror("Error", "The default summary cannot be deleted.")
            return
        if messagebox.askyesno("Delete", f"Delete entry '{key}'?"):
            base_dir = os.path.dirname(self.current_file)
            try:
                paths = self.summaries.get(key, {})
                if isinstance(paths, dict):
                    summary_path = os.path.join(base_dir, paths.get("summary", ""))
                    cover_path = os.path.join(base_dir, paths.get("cover_letter", ""))
                    for path in [summary_path, cover_path]:
                        try:
                            if os.path.exists(path):
                                os.remove(path)
                        except Exception:
                            pass
                else:
                    # fallback if old format (just string path)
                    path = os.path.join(base_dir, paths)
                    if os.path.exists(path):
                        os.remove(path)
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting files:\n{e}")
            del self.summaries[key]
            self.dropdown["values"] = list(self.summaries.keys())
            self.text.delete("1.0", tk.END)
            self.summary_var.set("")
            self.current_key = None
            self.current_file_path = None
            self.save()

    def save_summary(self):
        if not self.current_key or self.current_key not in self.summaries:
            return

        base_path = os.path.dirname(self.current_file)
        paths = self.summaries[self.current_key]

        summary_path = os.path.join(base_path, paths.get("summary", ""))
        cover_path = os.path.join(base_path, paths.get("cover_letter", ""))

        try:
            # Save summary
            summary_content = self.text.get("1.0", tk.END).strip()
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(summary_content)

            # Save cover letter
            cover_content = self.cover_letter_text.get("1.0", tk.END).strip()
            with open(cover_path, "w", encoding="utf-8") as f:
                f.write(cover_content)

            messagebox.showinfo("Saved", f"Summary and cover letter for '{self.current_key}' saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save files:\n{e}")

    def get_data(self):
        return self.summaries
