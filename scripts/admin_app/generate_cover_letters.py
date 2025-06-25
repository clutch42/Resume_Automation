from fpdf import FPDF
import os
from utils import load_cover_letter

def save_as_pdf(text, filename):
    safe_text = text.replace("’", "'").replace("“", '"').replace("”", '"').replace("—", "-")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=25.4)
    pdf.set_margins(left=25.4, top=25.4, right=25.4)
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    for line in safe_text.split('\n'):
        pdf.multi_cell(0, 6, line)
    pdf.output(filename)
    print(f"Saved cover letter as {filename}")

def generate_cover_letter_pdf(user_folder_path, professional_title, company_name, output_path):
    # Load the cover letter template text from utils
    cover_letter_text = load_cover_letter(user_folder_path, professional_title, company_name)
    if not cover_letter_text or not cover_letter_text.strip():
        print("No cover letter content found, skipping PDF generation.")
        return False

    # Replace the placeholder with the actual company name
    formatted_text = cover_letter_text.replace("{company}", company_name)

    # Construct the full file path
    save_as_pdf(formatted_text, output_path)
    return True
