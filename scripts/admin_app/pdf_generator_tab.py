import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from base_tab import BaseTab
from scripts.admin_app.pull_details import process_description, process_description_with_openai
import os
from resume_creator import generate_auto_resume
from generate_cover_letters import generate_cover_letter_pdf
from utils import load_skills
from scripts.openai_api_calls import get_skills

class PDFGeneratorTab(BaseTab):
    def __init__(self, notebook):
        super().__init__(notebook, "PDF Generator", default_filename=None)
        self.use_openai_var = tk.BooleanVar(value=False)
        self.result_data = None
        self.description_processed = False
        self.link_entries = {}
        self.build_ui()

    def build_ui(self):
        frame = self.frame

        # Output path selection
        output_frame = ttk.Frame(frame)
        output_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(output_frame, text="Output Path:").pack(side="left")
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=60)
        self.output_entry.pack(side="left", padx=5)
        ttk.Button(output_frame, text="Browse", command=self.browse_output_folder).pack(side="left")

        # Checkbox to use OpenAI API
        openai_frame = ttk.Frame(frame)
        openai_frame.pack(fill="x", padx=10, pady=5)

        openai_checkbox = ttk.Checkbutton(
            openai_frame,
            text="Use OpenAI API for job description analysis",
            variable=self.use_openai_var
        )
        openai_checkbox.pack(side="left")

        # Large text input
        self.text = tk.Text(frame, wrap="word", height=20)
        self.text.pack(fill="both", expand=True, padx=10, pady=5)

        # Buttons: Analyze and Create PDFs
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)

        self.analyze_button = ttk.Button(button_frame, text="Analyze", command=self.analyze_description)
        self.analyze_button.pack(side="left", pady=5)

        self.compare_button = ttk.Button(button_frame, text="Compare Skills", command=self.compare_skills)
        self.compare_button.pack(side="left", pady=5)
        self.compare_button.state(['disabled'])

        self.pdf_button = ttk.Button(button_frame, text="Create PDFs", command=self.generate_pdfs)
        self.pdf_button.pack(side="left", pady=5)
        self.pdf_button.state(['disabled'])

        # Links display (read-only)
        links_frame = ttk.Frame(frame)
        links_frame.pack(pady=10, padx=10, anchor="w")

        for key, label_text in [("linkedin", "LinkedIn:"), ("github", "GitHub:"), ("portfolio", "Portfolio:")]:
            ttk.Label(links_frame, text=label_text).pack(anchor="w")
            entry = ttk.Entry(links_frame, width=80, state="readonly")
            entry.pack(anchor="w", pady=2)
            entry.bind("<Button-1>", self.copy_to_clipboard)  # <-- bind click here
            self.link_entries[key] = entry
        
        self.load_personal_links()

    def browse_output_folder(self):
            folder = filedialog.askdirectory(title="Select Output Folder")
            if folder:
                self.output_var.set(folder)
            self.update_pdf_button_state()

    def update_compare_button_state(self):
        if self.description_processed:
            self.compare_button.state(['!disabled'])
        else:
            self.compare_button.state(['disabled'])

    def update_pdf_button_state(self):
        output_path = self.output_var.get().strip()
        if self.description_processed and os.path.isdir(output_path):
            self.pdf_button.state(['!disabled'])
        else:
            self.pdf_button.state(['disabled'])

    def analyze_description(self):
        job_text = self.text.get("1.0", tk.END).strip()
        app = self.frame._root().app_instance
        user_folder_path = getattr(app, "user_folder_path", None)

        try:
            if self.use_openai_var.get():
                result = process_description_with_openai(job_text, user_folder_path)
            else:
                result = process_description(job_text, user_folder_path)

            if result is False:
                return

            self.result_data = result
            self.description_processed = True
            self.update_compare_button_state()
            self.update_pdf_button_state()
            messagebox.showinfo("Success", "Job description analyzed successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze job description:\n{e}")

    def generate_pdfs(self):
        output_path = self.output_var.get().strip()
        app = self.frame._root().app_instance
        user_folder_path = getattr(app, "user_folder_path", None)

        if not user_folder_path:
            messagebox.showerror("Error", "No user folder loaded.")
            return

        if not os.path.isdir(output_path):
            messagebox.showerror("Error", "Please specify a valid output directory.")
            return

        result = self.result_data or {}

        filename = "Brian_Engel_Resume.pdf"
        full_output_path = os.path.join(output_path, filename)
        generate_auto_resume(user_folder_path, result, full_output_path)

        professional_title = result.get("professional_title", "Engineer")
        company_name = result.get("company_name", "Hiring Manager")
        full_cover_path = os.path.join(output_path, "Brian_Engel_Cover_Letter.pdf")
        generate_cover_letter_pdf(user_folder_path, professional_title, company_name, full_cover_path)

        messagebox.showinfo("Success", "PDFs generated successfully.")

    def compare_skills(self):
        user_folder_path = getattr(self.frame._root().app_instance, "user_folder_path", None)
        if not user_folder_path:
            messagebox.showerror("Error", "No user folder loaded.")
            return

        job_description = self.text.get("1.0", "end").strip()
        if not job_description:
            messagebox.showerror("Error", "No job description text entered.")
            return

        skills_json = load_skills(user_folder_path)

        alias_to_skill = {}
        for category_skills in skills_json.values():
            for skill_obj in category_skills:
                canonical_name = skill_obj["name"]
                alias_to_skill[canonical_name.lower()] = canonical_name
                for alias in skill_obj.get("aliases", []):
                    alias_to_skill[alias.lower()] = canonical_name

        openai_skills = get_skills(job_description)

        matched = []
        unmatched = []

        for skill in openai_skills:
            skill_lower = skill.lower()
            if skill_lower in alias_to_skill:
                canonical = alias_to_skill[skill_lower]
                if canonical not in matched:
                    matched.append(canonical)
            else:
                if skill not in unmatched:
                    unmatched.append(skill)

        msg = "Matched Skills:\n" + "\n".join(matched) if matched else "No matched skills found."
        msg += "\n\nUnmatched Skills:\n" + "\n".join(unmatched) if unmatched else "\nNo unmatched skills found."
        messagebox.showinfo("Skills Comparison Results", msg)
    
    def load_personal_links(self):
        user_folder_path = getattr(self.frame._root().app_instance, "user_folder_path", None)
        if not user_folder_path:
            return

        try:
            file_path = os.path.join(user_folder_path, "personal_info.json")
            with open(file_path, "r") as f:
                personal_info = json.load(f)
            for key in ["linkedin", "github", "portfolio"]:
                value = personal_info.get(key, "")
                entry = self.link_entries[key]
                entry.config(state="normal")
                entry.delete(0, tk.END)
                entry.insert(0, value)
                entry.config(state="readonly")
        except Exception as e:
            print(f"[ERROR] Failed to load personal links: {e}")

    def copy_to_clipboard(self, event):
        widget = event.widget
        text = widget.get()
        if text:
            self.frame.clipboard_clear()
            self.frame.clipboard_append(text)
            original_fg = widget.cget("foreground")
            widget.config(foreground="orange")
            widget.after(500, lambda: widget.config(foreground=original_fg))

