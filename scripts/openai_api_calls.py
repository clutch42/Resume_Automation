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
        return _cached_data

    system_prompt = """You extract structured data from job descriptions.
Return a raw JSON object (no markdown or backticks) with three keys:
- 'company': name of the company, or 'Not found' if not mentioned
- 'experience': minimum required experience as a string with unit of time, or 'Not found'
- 'skills': a Python list of the skills mentioned

Example format:
{
    "company": "Acme Corp",
    "experience": "3 years",
    "skills": ["Python", "Django", "REST APIs"]
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
    Wiraa logo
Wiraa
Share
Show more options
Software Engineer (Java/Python)
United States · 2 hours ago · Over 100 people clicked apply
Promoted by hirer · Responses managed off LinkedIn


 Remote
Matches your job preferences, workplace type is Remote.

 Full-time
Matches your job preferences, job type is Full-time.

Apply

Save
Save Software Engineer (Java/Python) at Wiraa
Software Engineer (Java/Python)
Wiraa · United States (Remote)

Apply

Save
Save Software Engineer (Java/Python) at Wiraa
Show more options
How your profile and resume fit this job
Get AI-powered advice on this job and more exclusive features with Premium. Try Premium for $0




Tailor my resume to this job

Am I a good fit for this job?

How can I best position myself for this job?

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

Design, develop, test, and maintain software solutions using relevant programming languages
Provide technical support and guidance to internal teams and external customers
Participate in system analysis, design, documentation, and testing activities
Collaborate with cross-disciplinary teams to define system requirements and design approaches
Support system performance testing and optimize resource efficiency, stability, and scalability
Maintain an in-depth understanding of Tangram Flex’s products, including Tangram Pro, and their application within customer environments
Contribute to building and enhancing software products, customer systems, and demonstration environments
Communicate technical concepts effectively to both technical and non-technical stakeholders
Address and resolve customer issues promptly, ensuring alignment with company values and objectives
Participate in Agile ceremonies such as sprint planning, reviews, and integration events
Document technical processes and project progress clearly and accurately
Benefits

Remote, hybrid, or on-site work options at our Dayton, Ohio, location
Flexible working hours and generous paid time off
Employer-paid medical, dental, and vision insurance
Short and long-term disability insurance coverage
Access to group-rated plans for life, disability, and pet insurance
Supportive work environment fostering transparency, collaboration, and well-being
Engaging employee events for social interaction and knowledge sharing
Opportunities for professional development and career growth
Equal Opportunity
Tangram Flex is an Affirmative Action and Equal Opportunity Employer. We are committed to creating an inclusive environment where all qualified candidates receive equal consideration for employment regardless of race, color, national origin, religion, age, disability status, genetics, protected veteran status, sex, sexual orientation, gender identity or expression, or any other characteristic protected by federal, state, or local laws.


Desired Skills and Experience
Information Technology
    """

    print("Company:", get_company(sample_description))
    print("Experience:", get_experience(sample_description))
    print("Skills:", get_skills(sample_description))