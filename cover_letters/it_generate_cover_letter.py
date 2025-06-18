from docx import Document
from fpdf import FPDF
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generate_cover_letter(company_name):
    return f"""Dear Hiring Manager,

I am excited to apply for opportunities at {company_name}. As a recent Computer Science graduate, I am eager to begin my career in the IT field. Although I have not held a formal IT role, \
my experience in customer-facing positions has helped me develop strong communication, problem-solving, and teamwork skills, which are essential for success in IT support and operational roles.

During my time at Walmart and Lucky's Pub, I gained valuable experience managing priorities, working effectively under pressure, and assisting and training team members. These skills, combined \
with my technical knowledge in scripting, DevOps basics, cloud services, and troubleshooting, prepare me to contribute to your IT team.

I hold CompTIA A+ and AWS Cloud Practitioner certifications, and I am committed to continuous learning and professional growth. I look forward to the opportunity to apply my skills and enthusiasm \
to support and advance the technology initiatives at {company_name}.

Thank you for considering my application. I would welcome the chance to discuss how I can be a valuable asset to your team.

Sincerely,  
Brian Engel  
(832) 888-6076  
brian.engel4242@gmail.com  
"""

def save_as_docx(text, filename):
    doc = Document()
    for line in text.split('\n'):
        p = doc.add_paragraph(line)
        p.paragraph_format.space_after = Pt(0)
    doc.save(filename)
    print(f"Saved cover letter as {filename}")

def save_as_pdf(text, filename):
    # Replace curly apostrophes and other Unicode characters with ASCII equivalents
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


def main():
    company = input("Enter the company name: ")
    letter_text = generate_cover_letter(company)
    print("\nChoose output format:")
    print("1. Word document (.docx)")
    print("2. PDF")
    choice = input("Enter 1 or 2: ").strip()

    if choice == '1':
        save_as_docx(letter_text, "Cover_Letter.docx")
    elif choice == '2':
        save_as_pdf(letter_text, "Cover_Letter.pdf")
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
