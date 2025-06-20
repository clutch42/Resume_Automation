import json

def load_skills(skills_file_path="../data/skills.json"):
    try:
        with open(skills_file_path, "r", encoding="utf-8") as f:
            skills_dict = json.load(f)
        return skills_dict
    except Exception as e:
        print(f"Error loading skills: {e}")
        return {}

def load_experience(experience_file_path="../data/experience.json"):
    try:
        with open(experience_file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading experience data: {e}")
        return []

def load_education(education_file_path="../data/education.json"):
    try:
        with open(education_file_path, "r", encoding="utf-8") as f:
            education_list = json.load(f)
        return education_list
    except Exception as e:
        print(f"Error loading education data: {e}")
        return []
    
def load_certifications(certifications_file_path="../data/certifications.json"):
    try:
        with open(certifications_file_path, "r", encoding="utf-8") as f:
            certifications = json.load(f)
        return certifications
    except Exception as e:
        print(f"Error loading certifications: {e}")
        return []

def load_projects(projects_file_path="../data/projects.json"):
    try:
        with open(projects_file_path, "r", encoding="utf-8") as f:
            projects = json.load(f)
        return projects
    except Exception as e:
        print(f"Error loading projects: {e}")
        return []

def load_personal_info(personal_info_path="../data/personal_info.json"):
    try:
        with open(personal_info_path, "r", encoding="utf-8") as f:
            personal_info = json.load(f)
        return personal_info
    except Exception as e:
        print(f"Error loading personal info: {e}")
        return {}
    
def load_job_description(json_path="../output/output.json"):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading job description: {e}")
        return {}

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