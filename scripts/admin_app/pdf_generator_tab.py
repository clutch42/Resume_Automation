import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from base_tab import BaseTab  # Keep for layout consistency
from scripts.admin_app.pull_details import process_description
import os
from resume_creator import generate_auto_resume
from generate_cover_letters import generate_cover_letter_pdf

class PDFGeneratorTab(BaseTab):
    def __init__(self, notebook):
        super().__init__(notebook, "PDF Generator", default_filename=None)  # no file needed
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

        # Large text input
        self.text = tk.Text(frame, wrap="word", height=20)
        self.text.pack(fill="both", expand=True, padx=10, pady=5)

        # Button to generate PDFs
        ttk.Button(frame, text="Generate PDFs", command=self.generate_pdfs).pack(pady=10)

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

        result = process_description(text, user_folder_path)
        if result is False:
            return
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
