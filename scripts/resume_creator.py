import json
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch

def create_resume_heading(name, professional_title=None):
    styles = getSampleStyleSheet()

    # Custom styles
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=24,
    )
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    flowables = []
    flowables.append(Paragraph(name, name_style))
    if professional_title:
        flowables.append(Paragraph(professional_title, title_style))

    contact_info = (
        '<a href="tel:8328886076"><font color="blue">(832)-888-6076</font></a> | '
        '<a href="mailto:brian.engel4242@gmail.com"><font color="blue">brian.engel4242@gmail.com</font></a> | '
        "Houston, TX, 77077 | "
        '<a href="https://www.linkedin.com/in/brian-david-engel/"><font color="blue">LinkedIn</font></a> | '
        '<a href="https://github.com/clutch42"><font color="blue">GitHub</font></a> | '
        '<a href="https://thebrianengel.com/"><font color="blue">Portfolio</font></a>'
    )
    flowables.append(Paragraph(contact_info, contact_style))
    return flowables

def generate_resume(json_path, output_pdf):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    name = "Brian Engel"
    professional_title = data.get("professional_title")
    # ... other data like contact info, skills, etc.
    story = []

    # Add heading section flowables
    story.extend(create_resume_heading(name, professional_title))

    # TODO: Add other sections like skills, experience, etc. here, extending story with their flowables

    doc = SimpleDocTemplate(output_pdf, pagesize=LETTER,
                            rightMargin=60, leftMargin=60,
                            topMargin=60, bottomMargin=60)
    doc.build(story)

if __name__ == "__main__":
    generate_resume("output.json", "test_resume.pdf")