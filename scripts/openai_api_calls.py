from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_cached_job_description = None
_cached_data = {}

def _extract_all(job_description: str):
    global _cached_job_description, _cached_data

    if job_description == _cached_job_description:
        print("✅ Using cached result")
        return _cached_data

    print("📡 Calling OpenAI API")
    system_prompt = """You extract structured data from job descriptions.
Return a raw JSON object (no markdown or backticks) with three keys:
- 'company': the normalized name of the company (remove suffixes like Inc., LLC, Ltd., Corp., and any symbols such as ®, ™), or 'Not found' if not mentioned.
- 'experience': minimum required experience as a string with unit of time, or 'Not found'
- 'skills': a Python list of the skills mentioned, including technical skills such as programming languages, tools, frameworks, technologies, and software engineering and IT practices or methodologies.
Do NOT include soft skills like communication, teamwork, leadership, or other interpersonal skills.

Example format:
{
    "company": "Acme Corp",
    "experience": "3 years",
    "skills": ["Python", "Django", "REST APIs", "Testing and Validation", "Troubleshooting and Debugging"]
}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": job_description}
        ],
        max_tokens=300,
        temperature=0.2,
    )

    raw_content = response.choices[0].message.content.strip()
    try:
        result = json.loads(raw_content)
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON from model response:")
        print(raw_content)
        raise
    _cached_job_description = job_description
    _cached_data = result
    return result

def get_company(job_description):
    return _extract_all(job_description).get("company", "Not found")

def get_experience(job_description):
    return _extract_all(job_description).get("experience", "Not found")

def get_skills(job_description):
    return _extract_all(job_description).get("skills", [])

if __name__ == "__main__":
    print("Running test...")

    sample_description = """

About the job
About The Company

Tangram Flex is a leading provider of innovative software solutions dedicated to advancing national security and technological innovation. Our mission is to enable the development, verification, and deployment of critical systems that support our nation's defense and security objectives.
We specialize in delivering high-performance, reliable, and scalable software products that meet the complex needs of government and industry clients. Our team is committed to fostering a collaborative and inclusive work environment that promotes continuous learning, innovation, and excellence. With a focus on cutting-edge technologies and standards, Tangram Flex strives to transform the way software challenges are addressed in the defense sector, ensuring our clients stay ahead in a rapidly evolving landscape.
About The Role

We are seeking a highly skilled Software Engineer with over five years of experience to join our dynamic team. In this role, you will serve as a key technical contributor responsible for designing, developing, and maintaining sophisticated software solutions that support our critical systems. You will work closely with cross-functional teams, including systems engineers, product managers, and customer stakeholders, to deliver innovative and reliable software that meets stringent performance and security standards. Your expertise will be instrumental in troubleshooting complex integration challenges, providing technical guidance to customers, and contributing to the continuous improvement of our software products. This position offers the opportunity to work in a collaborative environment, either remotely, hybrid, or on-site at our Dayton, Ohio, location, contributing to projects that directly impact national security.
Qualifications

Bachelor's Degree in Computer Engineering, Electrical Engineering, Systems Engineering, or a related technical field
Current or recent U.S. Government Security Clearance, or the ability to obtain and maintain one
U.S. citizenship is mandatory
Deep experience with programming languages such as C, C++, Java, Python, or Rust
Minimum of 5 years of software development or engineering experience in a collaborative team environment
Strong understanding of Object-Oriented Design principles
Experience with system testing, performance analysis, and troubleshooting
Excellent communication skills to articulate technical concepts to diverse audiences
Ability to work independently and as part of a team in a fast-paced environment
Responsibilities
    """

    print("Company:", get_company(sample_description))
    print("Experience:", get_experience(sample_description))
    print("Skills:", get_skills(sample_description))