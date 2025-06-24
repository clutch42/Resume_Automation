import json
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from utils import load_skills, load_experience, load_education, load_certifications, load_projects, load_personal_info, load_job_description, load_summary

MAX_SKILLS_PER_CATEGORY = 5

MARGINS = 40

BIG_TEXT = 18
MEDIUM_TEXT = 12
SMALL_TEXT = 10
TINY_TEXT = 9

NO_SPACE = 0
LITTLE_SPACE = 1
MEDIUM_SPACE = 3
BIG_SPACE = 6
HUGE_SPACE = 12

def create_resume_heading(personal_info, professional_title=None):
    styles = getSampleStyleSheet()

    # Custom styles
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=BIG_TEXT,
        alignment=TA_CENTER,
        spaceAfter=HUGE_SPACE,
    )
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=MEDIUM_TEXT,
        alignment=TA_CENTER,
        spaceAfter=MEDIUM_SPACE,
    )
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=SMALL_TEXT,
        alignment=TA_CENTER,
        spaceAfter=BIG_SPACE
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

def create_resume_summary(user_folder_path, professional_title):
    styles = getSampleStyleSheet()

    # Bold "Summary" style
    heading_style = ParagraphStyle(
        'SummaryHeading',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=MEDIUM_TEXT,
        alignment=TA_LEFT,
        spaceAfter=MEDIUM_SPACE
    )
    # Normal paragraph style for the summary text
    summary_style = ParagraphStyle(
        'SummaryText',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=SMALL_TEXT,
        alignment=TA_LEFT,
        spaceAfter=BIG_SPACE
    )
    summary_text = load_summary(user_folder_path, professional_title)
    flowables = []
    if summary_text:
        flowables.append(Paragraph("Summary", heading_style))
        flowables.append(HRFlowable(width="100%", thickness=1, lineCap='round', color='black', spaceBefore=NO_SPACE, spaceAfter=MEDIUM_SPACE))
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
        spaceAfter=MEDIUM_SPACE,
    )
    line_style = ParagraphStyle(
        'SkillLine',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=SMALL_TEXT,
        spaceAfter=MEDIUM_SPACE,
    )
    
    flowables = []
    flowables.append(Paragraph("Skills", heading_style))
    flowables.append(HRFlowable(width="100%", thickness=1, lineCap='round', color='black', spaceBefore=NO_SPACE, spaceAfter=MEDIUM_SPACE))
    
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
        spaceBefore=BIG_SPACE,
        spaceAfter=MEDIUM_SPACE,
    )
    job_title_style = ParagraphStyle(
        'JobTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=SMALL_TEXT + 1,
        spaceAfter=LITTLE_SPACE,
    )
    job_details_style = ParagraphStyle(
        'JobDetails',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=TINY_TEXT,
        spaceAfter=LITTLE_SPACE
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=TINY_TEXT,
        leftIndent=12,
        bulletIndent=0,
        spaceAfter=LITTLE_SPACE,
    )

    flowables = []
    flowables.append(Paragraph("Experience", heading_style))
    flowables.append(HRFlowable(width="100%", thickness=1, color='black', spaceBefore=NO_SPACE, spaceAfter=MEDIUM_SPACE))

    available_width = LETTER[0] - 2 * MARGINS - 10

    for job in experience_data:
        title = job.get("title", "")
        employer = job.get("employer", "")
        start = job.get("start_date", "")
        end = job.get("end_date", "")
        location = job.get("location", "")
        bullets = job.get("bullets", [])

        left = f"{title} — {employer}"
        right = f"{start} to {end} | {location}"

        right_width = stringWidth(right, "Times-Roman", TINY_TEXT)

        table = Table(
            [[Paragraph(left, job_title_style), Paragraph(right, job_details_style)]],
            colWidths=[available_width - right_width, right_width],
            style=[
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]
        )
        table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))

        flowables.append(table)

        for bullet in bullets:
            flowables.append(Paragraph(f"• {bullet}", bullet_style))

        flowables.append(Spacer(1, MEDIUM_SPACE))

    return flowables

def create_resume_education(education_list):
    styles = getSampleStyleSheet()
    
    heading_style = ParagraphStyle(
        'EducationHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=MEDIUM_TEXT,
        alignment=TA_LEFT,
        spaceBefore=BIG_SPACE,
        spaceAfter=MEDIUM_SPACE,
    )
    degree_style = ParagraphStyle(
        'DegreeStyle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=SMALL_TEXT + 1,
        spaceAfter=LITTLE_SPACE,
    )
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=TINY_TEXT,
        spaceAfter=LITTLE_SPACE,
    )
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=TINY_TEXT,
        leftIndent=12,
        bulletIndent=0,
        spaceAfter=LITTLE_SPACE,
    )
    
    flowables = []
    flowables.append(Paragraph("Education", heading_style))
    flowables.append(HRFlowable(width="100%", thickness=1, lineCap='round', color='black', spaceBefore=NO_SPACE, spaceAfter=MEDIUM_SPACE))
    
    available_width = LETTER[0] - 2 * MARGINS - 10

    for edu in education_list:
        school = f"{edu['degree']}, {edu['school']} (GPA: {edu['gpa']})"
        dates = f"{edu['start_date']} — {edu['end_date']}"

        dates_width = stringWidth(dates, "Times-Roman", TINY_TEXT)

        table = Table(
            [[Paragraph(school, degree_style), Paragraph(dates, info_style)]],
            colWidths=[available_width - dates_width, dates_width],
            style=[
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ]
        )

        flowables.append(table)
        
        for bullet in edu.get('details', []):
            flowables.append(Paragraph(f"• {bullet}", bullet_style))
        
        flowables.append(Spacer(1, MEDIUM_SPACE))  # space after each education block

    return flowables

def create_resume_certifications(certifications):
    styles = getSampleStyleSheet()
    
    heading_style = ParagraphStyle(
        'CertificationsHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=MEDIUM_TEXT,
        alignment=TA_LEFT,
        spaceBefore=BIG_SPACE,
        spaceAfter=MEDIUM_SPACE,
    )
    cert_style = ParagraphStyle(
        'CertificationItem',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=SMALL_TEXT,
        spaceAfter=MEDIUM_SPACE,
    )
    cert_date_style = ParagraphStyle(
        'CertificationItem',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=TINY_TEXT,
        spaceAfter=MEDIUM_SPACE,
    )
    
    flowables = []
    flowables.append(Paragraph("Certifications", heading_style))
    flowables.append(HRFlowable(width="100%", thickness=1, lineCap='round', color='black', spaceBefore=NO_SPACE, spaceAfter=MEDIUM_SPACE))
    
    available_width = LETTER[0] - 2 * MARGINS - 10

    for cert in certifications:
        name = cert.get("name", "Unknown Certification")
        date = cert.get("date", "")
        url = cert.get("link")
        
        date_width = stringWidth(date, "Times-Roman", SMALL_TEXT)

        if url:
            name_para = Paragraph(f'<a href="{url}"><font color="blue">{name}</font></a>', cert_style)
        else:
            name_para = Paragraph(name, cert_style)

        date_para = Paragraph(date, cert_date_style)
        
        table = Table(
            [[name_para, date_para]],
            colWidths=[available_width - date_width, date_width],
            style=[
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ]
        )

        flowables.append(table)
    
    return flowables

def create_resume_projects(projects):
    projects_page_url = projects.get("projects_page_url")
    projects = projects.get("projects", [])
    styles = getSampleStyleSheet()
    
    heading_style = ParagraphStyle(
        'ProjectsHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=MEDIUM_TEXT,
        alignment=TA_LEFT,
        spaceBefore=BIG_SPACE,
        spaceAfter=MEDIUM_SPACE,
    )
    project_title_style = ParagraphStyle(
        'ProjectTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=SMALL_TEXT,
        alignment=TA_LEFT,
        spaceAfter=LITTLE_SPACE,
    )
    bullet_style = ParagraphStyle(
        'ProjectBullet',
        parent=styles['Normal'],
        fontSize=TINY_TEXT,
        leftIndent=12,
        bulletIndent=0,
        spaceAfter=LITTLE_SPACE,
    )
    
    flowables = []

    if projects_page_url:
        heading_text = f'Projects – <a href="{projects_page_url}"><font color="blue">Projects Page</font></a>'
    else:
        heading_text = "Projects"

    flowables.append(Paragraph(heading_text, heading_style))
    flowables.append(HRFlowable(width="100%", thickness=1, lineCap='round', color='black', spaceBefore=NO_SPACE, spaceAfter=MEDIUM_SPACE))
    
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
        flowables.append(Spacer(1, LITTLE_SPACE))

    return flowables

def generate_auto_resume(user_folder_path, job_data, output_pdf):
    professional_title = job_data.get("professional_title")
    matched_skills = job_data.get("matched_skills", {})
    personal_info = load_personal_info(user_folder_path)
    skills_dict = load_skills(user_folder_path)
    experience_data = load_experience(user_folder_path)
    education_data = load_education(user_folder_path)
    certifications = load_certifications(user_folder_path)
    projects = load_projects(user_folder_path)

    story = []

    # Add heading section flowables
    story.extend(create_resume_heading(personal_info, professional_title))
    story.extend(create_resume_summary(user_folder_path, professional_title))
    story.extend(create_resume_skills(matched_skills, skills_dict))
    story.extend(create_resume_experience(experience_data))
    story.extend(create_resume_education(education_data))
    story.extend(create_resume_certifications(certifications))
    story.extend(create_resume_projects(projects))

    doc = SimpleDocTemplate(output_pdf, pagesize=LETTER,
                            rightMargin=MARGINS, leftMargin=MARGINS,
                            topMargin=MARGINS, bottomMargin=MARGINS)
    doc.build(story)

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