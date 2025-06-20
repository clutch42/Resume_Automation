import json
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from utils import load_skills, load_experience, load_education, load_certifications, load_projects, load_personal_info, load_job_description, load_summary

MAX_SKILLS_PER_CATEGORY = 6
MARGINS = 40
BIG_TEXT = 18
MEDIUM_TEXT = 12
SMALL_TEXT = 10
TINY_TEXT = 9

def create_resume_heading(personal_info, professional_title=None):
    styles = getSampleStyleSheet()

    # Custom styles
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=BIG_TEXT,
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=MEDIUM_TEXT,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=SMALL_TEXT,
        alignment=TA_CENTER,
        spaceAfter=10
    )

    flowables = []
    flowables.append(Paragraph(personal_info["name"], name_style))
    if professional_title:
        flowables.append(Paragraph(professional_title, title_style))

    contact_parts = []
    if personal_info.get("phone"):
        display = personal_info.get("phone_display", personal_info["phone"])
        contact_parts.append(f'<a href="tel:{personal_info["phone"]}"><font color="blue">{display}</font></a>')
    if personal_info.get("email"):
        contact_parts.append(f'<a href="mailto:{personal_info["email"]}"><font color="blue">{personal_info["email"]}</font></a>')
    if personal_info.get("location"):
        contact_parts.append(personal_info["location"])
    if personal_info.get("linkedin"):
        contact_parts.append(f'<a href="{personal_info["linkedin"]}"><font color="blue">LinkedIn</font></a>')
    if personal_info.get("github"):
        contact_parts.append(f'<a href="{personal_info["github"]}"><font color="blue">GitHub</font></a>')
    if personal_info.get("portfolio"):
        contact_parts.append(f'<a href="{personal_info["portfolio"]}"><font color="blue">Portfolio</font></a>')

    contact_info = " | ".join(contact_parts)
    flowables.append(Paragraph(contact_info, contact_style))
    return flowables

def create_resume_summary(professional_title):
    styles = getSampleStyleSheet()

    # Bold "Summary" style
    heading_style = ParagraphStyle(
        'SummaryHeading',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=MEDIUM_TEXT,
        alignment=TA_LEFT,
        spaceAfter=6
    )
    # Normal paragraph style for the summary text
    summary_style = ParagraphStyle(
        'SummaryText',
        parent=styles['Normal'],
        fontSize=SMALL_TEXT,
        alignment=TA_LEFT,
        spaceAfter=6
    )
    summary_text = load_summary(professional_title)
    flowables = []
    if summary_text:
        flowables.append(Paragraph("Summary", heading_style))
        flowables.append(HRFlowable(width="100%", thickness=1, lineCap='round', color='black', spaceBefore=0, spaceAfter=6))
        flowables.append(Paragraph(summary_text, summary_style))

    return flowables

def create_resume_skills(matched_skills, skills_dict):
    styles = getSampleStyleSheet()
    
    heading_style = ParagraphStyle(
        'SkillsHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=MEDIUM_TEXT,
        alignment=TA_LEFT,
        spaceAfter=6,
    )
    line_style = ParagraphStyle(
        'SkillLine',
        parent=styles['Normal'],
        fontSize=SMALL_TEXT,
        spaceAfter=3,
    )
    
    flowables = []
    flowables.append(Paragraph("Skills", heading_style))
    flowables.append(HRFlowable(width="100%", thickness=1, lineCap='round', color='black', spaceBefore=0, spaceAfter=6))
    
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

def create_resume_experience(experience_data):
    styles = getSampleStyleSheet()

    heading_style = ParagraphStyle(
        'ExperienceHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=MEDIUM_TEXT,
        alignment=TA_LEFT,
        spaceBefore=6,
        spaceAfter=6,
    )
    job_title_style = ParagraphStyle(
        'JobTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=SMALL_TEXT,
        spaceAfter=2,
    )
    job_details_style = ParagraphStyle(
        'JobDetails',
        parent=styles['Normal'],
        fontSize=SMALL_TEXT,
        spaceAfter=2,
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=TINY_TEXT,
        leftIndent=12,
        bulletIndent=0,
        spaceAfter=2,
    )

    flowables = []
    flowables.append(Paragraph("Experience", heading_style))
    flowables.append(HRFlowable(width="100%", thickness=1, color='black', spaceBefore=0, spaceAfter=6))

    for job in experience_data:
        title = job.get("title", "")
        employer = job.get("employer", "")
        start = job.get("start_date", "")
        end = job.get("end_date", "")
        location = job.get("location", "")
        bullets = job.get("bullets", [])

        header = f"{title} — {employer}"
        details = f"{start} to {end} | {location}"

        flowables.append(Paragraph(header, job_title_style))
        flowables.append(Paragraph(details, job_details_style))

        for bullet in bullets:
            flowables.append(Paragraph(f"• {bullet}", bullet_style))

        flowables.append(Spacer(1, 12))

    return flowables

def create_resume_education(education_list):
    styles = getSampleStyleSheet()
    
    heading_style = ParagraphStyle(
        'EducationHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=6,
    )
    degree_style = ParagraphStyle(
        'DegreeStyle',
        parent=styles['Normal'],
        fontName='Times-BoldItalic',
        fontSize=11,
        spaceAfter=4,
    )
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4,
    )
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=12,
        bulletIndent=6,
        spaceAfter=2,
    )
    
    flowables = []
    flowables.append(Paragraph("Education", heading_style))
    flowables.append(HRFlowable(width="100%", thickness=1, lineCap='round', color='black', spaceBefore=0, spaceAfter=12))
    
    for edu in education_list:
        degree_school = f"{edu.get('degree', '')}, {edu.get('school', '')} (GPA: {edu.get('gpa', 'N/A')})"
        flowables.append(Paragraph(degree_school, degree_style))
        
        dates = f"{edu.get('start_date', '')} — {edu.get('end_date', '')}"
        flowables.append(Paragraph(dates, info_style))
        
        for bullet in edu.get('details', []):
            flowables.append(Paragraph(f"• {bullet}", bullet_style))
        
        flowables.append(Spacer(1, 12))  # space after each education block

    return flowables

def create_resume_certifications(certifications):
    styles = getSampleStyleSheet()
    
    heading_style = ParagraphStyle(
        'CertificationsHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=6,
    )
    cert_style = ParagraphStyle(
        'CertificationItem',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
    )
    
    flowables = []
    flowables.append(Paragraph("Certifications", heading_style))
    flowables.append(HRFlowable(width="100%", thickness=1, lineCap='round', color='black', spaceBefore=0, spaceAfter=12))
    
    for cert in certifications:
        name = cert.get("name", "Unknown Certification")
        date = cert.get("date", "")
        url = cert.get("link")
        
        if url:
            # Name as clickable link
            cert_line = f'<a href="{url}"><font color="blue">{name}</font></a> — {date}'
        else:
            cert_line = f"{name} — {date}"
        
        flowables.append(Paragraph(cert_line, cert_style))
    
    return flowables

def create_resume_projects(projects):
    projects_page_url = projects.get("projects_page_url")
    projects = projects.get("projects", [])
    styles = getSampleStyleSheet()
    
    heading_style = ParagraphStyle(
        'ProjectsHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=6,
    )
    project_title_style = ParagraphStyle(
        'ProjectTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=4,
    )
    bullet_style = ParagraphStyle(
        'ProjectBullet',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=12,
        bulletIndent=0,
        spaceAfter=2,
    )
    
    flowables = []
    flowables.append(Paragraph("Projects", heading_style))
    flowables.append(HRFlowable(width="100%", thickness=1, lineCap='round', color='black', spaceBefore=0, spaceAfter=12))
    
    # Optional link to the projects page
    if projects_page_url:
        link_text = f'<a href="{projects_page_url}">Projects Page</a>'
        flowables.append(Paragraph(link_text, bullet_style))
        flowables.append(Spacer(1, 12))
    
    for proj in projects:
        # Project title with optional link
        if proj.get('url'):
            title = f'<a href="{proj["url"]}" color="blue">{proj["name"]}</a>'
        else:
            title = proj["name"]
        flowables.append(Paragraph(title, project_title_style))
        
        # Bullet points
        for detail in proj.get("details", []):
            flowables.append(Paragraph(f"• {detail}", bullet_style))
        flowables.append(Spacer(1, 8))

    return flowables

def generate_resume(json_path, output_pdf):
    job_data = load_job_description(json_path)
    professional_title = job_data.get("professional_title")
    matched_skills = job_data.get("matched_skills", {})
    personal_info = load_personal_info()
    skills_dict = load_skills()
    experience_data = load_experience()
    education_data = load_education()
    certifications = load_certifications()
    projects = load_projects()

    story = []

    # Add heading section flowables
    story.extend(create_resume_heading(personal_info, professional_title))
    story.extend(create_resume_summary(professional_title))
    story.extend(create_resume_skills(matched_skills, skills_dict))
    story.extend(create_resume_experience(experience_data))
    story.extend(create_resume_education(education_data))
    story.extend(create_resume_certifications(certifications))
    story.extend(create_resume_projects(projects))

    doc = SimpleDocTemplate(output_pdf, pagesize=LETTER,
                            rightMargin=MARGINS, leftMargin=MARGINS,
                            topMargin=MARGINS, bottomMargin=MARGINS)
    doc.build(story)

if __name__ == "__main__":
    generate_resume("../output/output.json", "../resumes/test_resume.pdf")