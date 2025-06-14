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

def main():
    with open("description.txt", "r", encoding="utf-8") as f:
        text = f.read()

    company_name = get_most_common_company(text)

    if company_name:
        print(f"Detected company name: {company_name}")
        with open("output.json", "w", encoding="utf-8") as outfile:
            json.dump({"company_name": company_name}, outfile, indent=2)
    else:
        print("No company name detected.")
        with open("output.json", "w", encoding="utf-8") as outfile:
            json.dump({"company_name": None}, outfile, indent=2)

if __name__ == "__main__":
    main()
