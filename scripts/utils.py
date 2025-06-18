import json

def load_skills(skills_file_path="../data/skills.json"):
    try:
        with open(skills_file_path, "r", encoding="utf-8") as f:
            skills_dict = json.load(f)
        return skills_dict
    except Exception as e:
        print(f"Error loading skills: {e}")
        return {}
