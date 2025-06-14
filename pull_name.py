import spacy
import re
import json
from collections import Counter

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

def main():
    with open("description.txt", "r", encoding="utf-8") as f:
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

    company_name = confirm_or_edit_company_name(company_name)

    output = {
        "company_name": company_name,
        "experience_ranges": experience_ranges if experience_ranges else None
    }

    with open("output.json", "w", encoding="utf-8") as outfile:
        json.dump(output, outfile, indent=2)

if __name__ == "__main__":
    main()
