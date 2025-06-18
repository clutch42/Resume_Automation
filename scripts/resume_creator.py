import json
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from utils import load_skills

MAX_SKILLS_PER_CATEGORY = 5

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

def load_summary(professional_title):
    try:
        with open("../data/summaries.json", "r", encoding="utf-8") as f:
            summary_map = json.load(f)

        summary_path = summary_map.get(professional_title) or summary_map.get("default")
        if summary_path:
            with open(f"../data/{summary_path}", "r", encoding="utf-8") as sf:
                return sf.read().strip()
    except Exception as e:
        print(f"Error loading summary: {e}")

    return None

def create_resume_summary(professional_title):
    styles = getSampleStyleSheet()

    # Bold "Summary" style
    heading_style = ParagraphStyle(
        'SummaryHeading',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=6
    )
    # Normal paragraph style for the summary text
    summary_style = ParagraphStyle(
        'SummaryText',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=12
    )
    summary_text = load_summary(professional_title)
    flowables = []
    if summary_text:
        flowables.append(Paragraph("Summary", heading_style))
        flowables.append(HRFlowable(width="100%", thickness=1, lineCap='round', color='black', spaceBefore=0, spaceAfter=12))
        flowables.append(Paragraph(summary_text, summary_style))

    return flowables

def create_resume_skills(matched_skills, skills_dict):
    styles = getSampleStyleSheet()
    
    heading_style = ParagraphStyle(
        'SkillsHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=6,
    )
    line_style = ParagraphStyle(
        'SkillLine',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
    )
    
    flowables = []
    flowables.append(Paragraph("Skills", heading_style))
    flowables.append(HRFlowable(width="100%", thickness=1, lineCap='round', color='black', spaceBefore=0, spaceAfter=12))
    
    for category, skill_objs in skills_dict.items():
        matched_names = set(matched_skills.get(category, []))
        filled = list(matched_names)

        # Fill with unmatched skill names until reaching MAX
        for skill in skill_objs:
            name = skill["name"]
            if name not in matched_names and len(filled) < MAX_SKILLS_PER_CATEGORY:
                filled.append(name)

        line = f"<b>{category}:</b> {', '.join(filled)}"
        flowables.append(Paragraph(line, line_style))

    return flowables

def generate_resume(json_path, output_pdf):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    name = "Brian Engel"
    professional_title = data.get("professional_title")
    matched_skills = data.get("matched_skills", {})
    skills_dict = load_skills()
    # ... other data like contact info, skills, etc.
    story = []

    # Add heading section flowables
    story.extend(create_resume_heading(name, professional_title))
    story.extend(create_resume_summary(professional_title))
    story.extend(create_resume_skills(matched_skills, skills_dict))

    doc = SimpleDocTemplate(output_pdf, pagesize=LETTER,
                            rightMargin=60, leftMargin=60,
                            topMargin=60, bottomMargin=60)
    doc.build(story)

if __name__ == "__main__":
    generate_resume("../output/output.json", "../resumes/test_resume.pdf")