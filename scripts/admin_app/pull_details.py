import spacy
import re
import json
import os
from collections import Counter, defaultdict
from scripts.admin_app.resume_creator import generate_resume
from utils import load_skills, load_professional_titles
import tkinter as tk
from tkinter import messagebox, simpledialog
from scripts.openai_api_calls import get_company, get_experience

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Helper to clean company names
def clean_name(name):
    # Remove common suffixes and punctuation
    name = re.sub(r"\b(Inc\.?|Corporation|Corp\.?|LLC|Ltd\.?|Co\.?|Company|Group)\b", "", name, flags=re.I)
    name = re.sub(r"[^\w\s&]", "", name)  # remove punctuation except &
    return name.strip()

def extract_candidates(text):
    doc = nlp(text)
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

    # Combined regex patterns for all requested forms:
    pattern = re.compile(
        r'\b(?:At|From|Join|Welcome to|Welcome at)\s+([A-Z][\w&\s.,-]{1,100}?)(?:,|\.| is| are|\n)|'  # existing pattern
        r'([A-Z][\w&\s.-]{1,100}?)(?: is| has| will|\'s)|'                                             # Company Name is/has/will/'s
        r'At\s+([A-Z][\w&\s.,-]{1,100}?)(?:,|\.|\n)|'                                                # At Company Name
        r'([A-Z][\w&\s.,-]{1,100}?)\s+(?:LLC|Inc\.?|Corporation|Corp\.?|Ltd\.?|Co\.?|Company|Group)', # Company Name with suffix
        re.I
    )

    matches = pattern.findall(text)
    # pattern.findall returns list of tuples with groups; flatten and clean:
    raw_names = []
    for match in matches:
        # match is a tuple with groups, get non-empty groups only
        for name in match:
            if name:
                raw_names.append(name)

    # Clean all names
    orgs_clean = [clean_name(name) for name in orgs]
    regex_clean = [clean_name(name) for name in raw_names]

    # Combine and filter out empty or very short names
    combined = [name for name in orgs_clean + regex_clean if len(name) > 2]

    return combined

def get_most_common_company(text):
    candidates = extract_candidates(text)
    if not candidates:
        return None
    counter = Counter(candidates)
    most_common = counter.most_common(1)[0][0]
    return most_common

def extract_experience_ranges(text):
    pattern = re.compile(
        r'\b(\d+\+?\s*(?:years?|months?))\b|'      # single values like "3 years", "5+ months"
        r'\b(\d+\s*(?:-|to)\s*\d+\s*(?:years?|months?))\b',  # ranges like "2-4 years", "2 to 6 months"
        re.I
    )
    matches = pattern.findall(text)
    
    # Flatten and clean matches (since findall returns tuples with groups)
    raw_matches = [m[0] or m[1] for m in matches]
    
    # Deduplicate while preserving order
    seen = set()
    unique_matches = []
    for match in raw_matches:
        normalized = match.lower().replace(" ", "")
        if normalized not in seen:
            seen.add(normalized)
            unique_matches.append(match.strip())
    
    return unique_matches

def confirm_or_edit_company_name(detected_name):
    while True:
        print(f"Detected company name: {detected_name}")
        user_input = input("Press Enter to accept or type a new company name: ").strip()

        if not user_input:
            return detected_name  # Accept original without confirmation

        confirm = input(f"Use '{user_input}'? (y/n): ").strip().lower()

        if confirm == "y":
            return user_input
        else:
            print("Let's try again.\n")

#def load_skills(filepath="../data/skills.json"):
#    with open(filepath, "r", encoding="utf-8") as f:
#        return json.load(f)
    
def extract_skills_from_text(resume_text, skills_dict):
    from collections import defaultdict

    found_skills = defaultdict(list)
    normalized_text = re.sub(r'(?<=\w)/(?=\w)', ' ', resume_text)
    lowered_text = normalized_text.lower()
    tokens = [w.strip('()",.:;') for w in lowered_text.split()]

    for category, skill_items in skills_dict.items():
        for item in skill_items:
            if isinstance(item, str):
                names_to_check = [item.lower()]
                display_name = item
            else:
                names_to_check = [item["name"].lower()] + [alias.lower() for alias in item.get("aliases", [])]
                display_name = item["name"]

            matched = False
            for name in names_to_check:
                if len(name.split()) > 1:
                    if name in lowered_text:
                        matched = True
                        break
                else:
                    if name in tokens:
                        matched = True
                        break

            if matched:
                # Prevent duplicates (optional)
                if display_name not in found_skills[category]:
                    found_skills[category].append(display_name)

    return dict(found_skills)

def clean_word(word):
    # Characters to strip only at start or end
    to_strip = '(),.:;'

    # Strip from start and end
    return word.strip(to_strip)

def confirm_experience_match(parent, company_name, experience_ranges):
    summary = ""
    if company_name:
        summary += f"Detected company name: {company_name}\n"
    else:
        summary += "No company name detected.\n"

    if experience_ranges:
        summary += f"Detected experience ranges: {experience_ranges}\n"
    else:
        summary += "No experience ranges detected.\n"

    summary += "Does the experience match your expectation?"

    return messagebox.askyesno("Experience Confirmation", summary, parent=parent)


def ask_professional_title(parent, titles):
    prompt = "Choose your professional title from the list by number, or type your own:\n"
    for idx, title in enumerate(titles, 1):
        prompt += f"{idx}: {title}\n"
    prompt += f"Enter choice (1-{len(titles)}) or type a title:"

    answer = simpledialog.askstring("Professional Title", prompt, parent=parent)
    if answer is None:
        return None  # User cancelled

    answer = answer.strip()
    if answer.isdigit():
        idx = int(answer)
        if 1 <= idx <= len(titles):
            return titles[idx - 1]
        else:
            messagebox.showerror("Invalid choice", "Invalid number choice. Using default None.")
            return None
    elif answer == "":
        return None
    else:
        return answer

def confirm_or_edit_company_name_popup(parent, detected_name):
    while True:
        prompt = f"Detected company name: {detected_name}\n\nPress OK to accept or enter a new company name:"
        user_input = simpledialog.askstring("Confirm Company Name", prompt, parent=parent)

        if user_input is None:  # User cancelled
            return None

        user_input = user_input.strip()

        if not user_input:
            # Accept original detected name
            return detected_name

        confirm = messagebox.askyesno("Confirm", f"Use '{user_input}'?", parent=parent)
        if confirm:
            return user_input
        else:
            # Loop again for new input
            continue

def process_description_with_openai(text, user_folder_path):
    root = tk.Tk()
    root.withdraw()

    is_blank = not text or not text.strip()

    if is_blank:
        titles = load_professional_titles(user_folder_path)
        professional_title = ask_professional_title(root, titles)
        company_name = confirm_or_edit_company_name_popup(root, "")

        root.destroy()

        return {
            "professional_title": professional_title,
            "company_name": company_name,
            "experience_ranges": None,
            "matched_skills": None
        }

    company_name = get_company(text)
    experience_ranges = get_experience(text)


    # Ask user if experience matches
    match = confirm_experience_match(root, company_name, experience_ranges)
    if not match:
        root.destroy()
        return False

    # Prompt for professional title
    titles = load_professional_titles(user_folder_path)
    professional_title = ask_professional_title(root, titles)

    company_name = confirm_or_edit_company_name_popup(root, company_name)
    skills_dict = load_skills(user_folder_path)
    matched_skills = extract_skills_from_text(text, skills_dict)

    root.destroy()  # close hidden root window

    output = {
        "professional_title": professional_title,
        "company_name": company_name,
        "experience_ranges": experience_ranges if experience_ranges else None,
        "matched_skills": matched_skills if matched_skills else None
    }

    # Continue with more processing or return data here
    return output

def process_description(text, user_folder_path):
    root = tk.Tk()
    root.withdraw()

    is_blank = not text or not text.strip()

    if is_blank:
        titles = load_professional_titles(user_folder_path)
        professional_title = ask_professional_title(root, titles)
        company_name = confirm_or_edit_company_name_popup(root, "")

        root.destroy()

        return {
            "professional_title": professional_title,
            "company_name": company_name,
            "experience_ranges": None,
            "matched_skills": None
        }

    company_name = get_most_common_company(text)
    experience_ranges = extract_experience_ranges(text)

    # Ask user if experience matches
    match = confirm_experience_match(root, company_name, experience_ranges)
    if not match:
        root.destroy()
        return False

    # Prompt for professional title
    titles = load_professional_titles(user_folder_path)
    professional_title = ask_professional_title(root, titles)

    company_name = confirm_or_edit_company_name_popup(root, company_name)
    skills_dict = load_skills(user_folder_path)
    matched_skills = extract_skills_from_text(text, skills_dict)

    root.destroy()  # close hidden root window

    output = {
        "professional_title": professional_title,
        "company_name": company_name,
        "experience_ranges": experience_ranges if experience_ranges else None,
        "matched_skills": matched_skills if matched_skills else None
    }

    # Continue with more processing or return data here
    return output

def main():
    with open("../description.txt", "r", encoding="utf-8") as f:
        text = f.read()

    company_name = get_most_common_company(text)
    experience_ranges = extract_experience_ranges(text)

    if company_name:
        print(f"Detected company name: {company_name}")
    else:
        print("No company name detected.")

    if experience_ranges:
        print(f"Detected experience ranges: {experience_ranges}")
    else:
        print("No experience ranges detected.")

    # Prompt to quit if experience doesn't match
    response = input("Does the experience match your expectation? (y/n) ")
    if response.lower() != 'y':
        print("Exiting as per user input due to experience mismatch.")
        return  # or sys.exit() if outside main()

    # Prompt for professional title
    titles = load_professional_titles()
    print("Choose your professional title from the list, or enter any other title:")
    for idx, title in enumerate(titles, 1):
        print(f"{idx}: {title}")

    title_input = input(f"Enter choice (1-{len(titles)}) or type a title: ").strip()

    if title_input.isdigit():
        idx = int(title_input)
        if 1 <= idx <= len(titles):
            professional_title = titles[idx - 1]
        else:
            print("Invalid number choice. Using default None.")
            professional_title = None
    elif title_input == '':
        professional_title = None
    else:
        professional_title = title_input

    company_name = confirm_or_edit_company_name(company_name)
    skills_dict = load_skills()
    matched_skills = extract_skills_from_text(text, skills_dict)

    print("Matched skills found:")
    if matched_skills:
        for category, skills in matched_skills.items():
            print(f"{category}: {', '.join(skills)}")
    else:
        print("No skills matched.")


    output = {
        "professional_title": professional_title,
        "company_name": company_name,
        "experience_ranges": experience_ranges if experience_ranges else None,
        "matched_skills": matched_skills if matched_skills else None
    }

    with open("../output/output.json", "w", encoding="utf-8") as outfile:
        json.dump(output, outfile, indent=2)

    generate_resume("../output/output.json", "../resumes/my_resume.pdf")
    

if __name__ == "__main__":
    main()
