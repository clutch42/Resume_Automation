from docx import Document
from fpdf import FPDF
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generate_cover_letter(company_name):
    return f"""Dear Hiring Manager,

I am excited to apply for opportunities at {company_name}. As a recent Computer Science graduate, I am eager to launch my career in software development. While I have not yet held a formal \
role in the field, my experience in the service industry has equipped me with strong communication, teamwork, and problem-solving skills that I believe are essential for success in any professional environment.

Through roles at Walmart and Lucky’s Pub, I developed the ability to work effectively under pressure, manage multiple priorities, and lead and train team members. These experiences have \
strengthened my collaboration and adaptability, qualities I am confident will help me thrive in a software development role.

Combined with my solid technical foundation in C++, Python, Java, and full-stack web development, I am passionate about continuous learning and committed to expanding my skills to contribute \
meaningfully to {company_name}. I am ready to learn quickly, collaborate with your team, and deliver quality results.

Thank you for considering my application. I look forward to the possibility of discussing how my background and soft skills align with your needs.

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
