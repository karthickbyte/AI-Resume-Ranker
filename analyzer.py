import re
import os

# Master skills list - AI will look for these in JD
SKILLS_LIST = [
    # Programming Languages
    "python", "java", "javascript", "c++", "c#", "ruby",
    "swift", "kotlin", "typescript", "php", "r",

    # Web Development
    "html", "css", "react", "angular", "vue", "django",
    "flask", "nodejs", "spring boot", "rest api",

    # Database
    "sql", "mysql", "postgresql", "mongodb", "oracle",
    "firebase", "redis",

    # Data Science & ML
    "machine learning", "deep learning", "nlp",
    "tensorflow", "keras", "pytorch", "pandas",
    "numpy", "scikit-learn", "statistics",
    "data visualization", "tableau", "power bi",

    # Cloud & DevOps
    "aws", "azure", "google cloud", "docker",
    "kubernetes", "jenkins", "git", "linux",
    "ci/cd", "bash",

    # Soft Skills
    "communication", "leadership", "problem solving",
    "teamwork", "time management", "critical thinking",

    # Tools
    "excel", "ms office", "jira", "figma",
    "photoshop", "postman"
]


def extract_skills_from_text(text):
    found_skills = []
    text_lower = text.lower()

    for skill in SKILLS_LIST:
        if skill.lower() in text_lower:
            if skill not in found_skills:
                found_skills.append(skill)

    return found_skills


def parse_job_description(jd_text):
    # Extract required skills
    required_skills = extract_skills_from_text(jd_text)

    # Extract job title
    job_title = "Not specified"
    for line in jd_text.split('\n'):
        line = line.strip()
        if line.lower().startswith('job title:'):
            job_title = line.split(':', 1)[1].strip()
            break

    # Extract experience
    experience = "Not specified"
    for line in jd_text.split('\n'):
        line = line.strip()
        if 'experience' in line.lower() and ':' in line:
            experience = line.split(':', 1)[1].strip()
            break

    return {
        "raw_text": jd_text,
        "job_title": job_title,
        "experience": experience,
        "required_skills": required_skills,
        "total_skills": len(required_skills)
    }


def read_jd_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return parse_job_description(content)
    except Exception as e:
        return f"Error reading JD: {str(e)}"


def read_all_jds(jd_folder):
    all_jds = []
    files = os.listdir(jd_folder)

    for file in sorted(files):
        if file.endswith('.txt'):
            path = f"{jd_folder}/{file}"
            jd_data = read_jd_from_file(path)
            jd_data['filename'] = file
            all_jds.append(jd_data)

    return all_jds