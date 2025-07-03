import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from base_tab import BaseTab  # Keep for layout consistency
from scripts.admin_app.pull_details import process_description, process_description_with_openai
import os
from resume_creator import generate_auto_resume
from generate_cover_letters import generate_cover_letter_pdf
from utils import load_skills
from scripts.openai_api_calls import get_skills

class PDFGeneratorTab(BaseTab):
    def __init__(self, notebook):
        super().__init__(notebook, "PDF Generator", default_filename=None)  # no file needed
        self.use_openai_var = tk.BooleanVar(value=False)
        self.result_data = None  # To track if process_description ran
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
        self.use_openai_var = tk.BooleanVar()
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

        # Button to generate PDFs
        ttk.Button(frame, text="Generate PDFs", command=self.generate_pdfs).pack(pady=10)

        # Skills Comparison button, disabled initially
        self.compare_button = ttk.Button(frame, text="Compare Skills", command=self.compare_skills)
        self.compare_button.pack(pady=5)
        self.compare_button.state(['disabled'])  # start disabled

        # Track if description has been processed yet
        self.description_processed = False

    def update_compare_button_state(self):
        # Enable button only if checkbox checked AND description processed
        if self.use_openai_var.get() and self.description_processed:
            self.compare_button.state(['!disabled'])
        else:
            self.compare_button.state(['disabled'])


    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_var.set(folder)

    def generate_pdfs(self):
        input_text = self.text.get("1.0", tk.END).strip()
        output_path = self.output_var.get().strip()

        #if not input_text:
        #   messagebox.showerror("Error", "Input text cannot be empty.")
        #   return
        if not output_path or not os.path.isdir(output_path):
            messagebox.showerror("Error", "Please specify a valid output directory.")
            return

        try:
            self.run_pdf_script(input_text, output_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDFs:\n{e}")

    def run_pdf_script(self, text, output_path):
        app = self.frame._root().app_instance
        user_folder_path = getattr(app, "user_folder_path", None)
        print(f"[DEBUG] Retrieved user_folder_path in PDFGeneratorTab: {user_folder_path}")

        if not user_folder_path:
            messagebox.showerror("Error", "No user folder loaded.")
            return

        result = None
        # example:
        if self.use_openai_var.get():
            result = process_description_with_openai(text, user_folder_path)  # your new func
        else:
            result = process_description(text, user_folder_path)

        if result is False:
            return

        # Mark description as processed
        self.description_processed = True
        self.update_compare_button_state()
        print(result)

        filename = "Brian_Engel_Resume.pdf"
        full_output_path = os.path.join(output_path, filename)
        generate_auto_resume(user_folder_path, result, full_output_path)

        # Generate cover letter PDF
        professional_title = result.get("professional_title")  # make sure this matches your result structure
        company_name = result.get("company_name") or "Hiring Manager"

        full_output_file = os.path.join(output_path, "Brian_Engel_Cover_Letter.pdf")
        generate_cover_letter_pdf(user_folder_path, professional_title, company_name, full_output_file)
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

        # Build alias -> canonical skill mapping
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

        # Show results to user
        msg = "Matched Skills:\n" + "\n".join(matched) if matched else "No matched skills found."
        msg += "\n\nUnmatched Skills:\n" + "\n".join(unmatched) if unmatched else "\nNo unmatched skills found."

        messagebox.showinfo("Skills Comparison Results", msg)
