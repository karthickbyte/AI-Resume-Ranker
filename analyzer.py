import re
import os
from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer, util

# Load .env file first
load_dotenv()

# Connect Gemini using .env key
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Load similarity model
print("Loading AI model...")
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
print("AI Model loaded! ✅")

# Master skills list
SKILLS_LIST = [
    # Programming Languages
    "python", "java", "javascript", "c++", "c#",
    "ruby", "swift", "kotlin", "typescript", "php",

    # Web Development
    "html", "css", "react", "angular", "vue",
    "django", "flask", "nodejs", "spring boot",
    "rest api", "api development",

    # Database
    "sql", "mysql", "postgresql", "mongodb",
    "oracle", "firebase", "redis",

    # Data Science & ML
    "machine learning", "deep learning", "nlp",
    "tensorflow", "keras", "pytorch", "pandas",
    "numpy", "scikit-learn", "statistics",
    "data visualization", "tableau", "power bi",
    "computer vision", "feature engineering",
    "data preprocessing", "jupyter notebook",
    "model deployment",

    # Data Analysis
    "data cleaning", "data analysis",
    "business intelligence", "reporting",
    "pivot tables",

    # Cloud & DevOps
    "aws", "azure", "google cloud", "docker",
    "kubernetes", "jenkins", "git", "linux",
    "ci/cd", "bash",

    # Soft Skills
    "communication", "leadership", "problem solving",
    "teamwork", "time management", "critical thinking",
    "analytical thinking", "attention to detail",

    # Tools
    "excel", "ms office", "jira", "figma",
    "photoshop", "postman",

    # Other
    "object oriented programming",
    "data structures", "algorithms",
    "unit testing", "agile", "scrum"
]

# Learning resources
LEARNING_RESOURCES = {
    "python": "freeCodeCamp Python course on YouTube",
    "java": "Java Programming by Tim Buchalka — Udemy",
    "sql": "SQLZoo.net or W3Schools SQL — Free",
    "machine learning": "Andrew Ng ML Course — Coursera Free Audit",
    "deep learning": "fast.ai free course — fast.ai",
    "nlp": "Hugging Face NLP Course — Free",
    "tensorflow": "TensorFlow official tutorials — tensorflow.org",
    "docker": "TechWorld with Nana Docker — YouTube",
    "aws": "AWS Free Tier + FreeCodeCamp AWS — YouTube",
    "git": "Git and GitHub crash course — YouTube",
    "power bi": "Microsoft Power BI learning — Free",
    "tableau": "Tableau Public free tutorials",
    "react": "React official docs + Traversy Media YouTube",
    "django": "Django for Beginners — Udemy",
    "communication": "Toastmasters or Coursera Communication Course",
    "leadership": "Leadership courses on Coursera — Free Audit",
    "excel": "Excel for beginners — YouTube GCFGlobal",
    "statistics": "Statistics by Khan Academy — Free",
    "kubernetes": "Kubernetes tutorial — TechWorld YouTube",
    "linux": "Linux command line basics — freeCodeCamp YouTube"
}


# =============================================
# JD PARSER FUNCTIONS
# =============================================

def extract_skills_from_text(text):
    found_skills = []
    text_lower = text.lower()
    for skill in SKILLS_LIST:
        if skill.lower() in text_lower:
            if skill not in found_skills:
                found_skills.append(skill)
    return found_skills


def parse_job_description(jd_text):
    required_skills = extract_skills_from_text(jd_text)

    job_title = "Not specified"
    for line in jd_text.split('\n'):
        line = line.strip()
        if line.lower().startswith('job title:'):
            job_title = line.split(':', 1)[1].strip()
            break

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


# =============================================
# SIMILARITY FUNCTIONS
# =============================================

def calculate_similarity(resume_text, jd_text):
    try:
        resume_vector = similarity_model.encode(
            resume_text,
            convert_to_tensor=True
        )
        jd_vector = similarity_model.encode(
            jd_text,
            convert_to_tensor=True
        )
        similarity = util.cos_sim(resume_vector, jd_vector)
        score = float(similarity) * 100
        return round(score, 2)
    except Exception as e:
        print(f"Similarity error: {e}")
        return 0.0


def get_similarity_label(score):
    if score >= 80:
        return "🟢 Excellent Match"
    elif score >= 60:
        return "🟡 Good Match"
    elif score >= 40:
        return "🟠 Average Match"
    else:
        return "🔴 Poor Match"


# =============================================
# SKILL GAP FUNCTIONS
# =============================================

def analyze_skill_gap(resume_text, required_skills):
    matched_skills = []
    missing_skills = []
    resume_lower = resume_text.lower()

    for skill in required_skills:
        if skill.lower() in resume_lower:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    total = len(required_skills)
    if total > 0:
        match_percentage = (len(matched_skills) / total) * 100
        gap_percentage = (len(missing_skills) / total) * 100
    else:
        match_percentage = 0
        gap_percentage = 0

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": round(match_percentage, 1),
        "gap_percentage": round(gap_percentage, 1),
        "total_required": total,
        "total_matched": len(matched_skills),
        "total_missing": len(missing_skills)
    }


def get_learning_suggestions(missing_skills):
    suggestions = {}
    for skill in missing_skills:
        skill_lower = skill.lower()
        if skill_lower in LEARNING_RESOURCES:
            suggestions[skill] = LEARNING_RESOURCES[skill_lower]
        else:
            suggestions[skill] = f"Search '{skill} tutorial' on YouTube"
    return suggestions


def get_gap_label(match_percentage):
    if match_percentage >= 80:
        return "🟢 Strong Candidate"
    elif match_percentage >= 60:
        return "🟡 Good Candidate"
    elif match_percentage >= 40:
        return "🟠 Average Candidate"
    else:
        return "🔴 Not Recommended"


def full_gap_analysis(resume_data, jd_data):
    gap = analyze_skill_gap(
        resume_data['full_text'],
        jd_data['required_skills']
    )
    suggestions = get_learning_suggestions(gap['missing_skills'])
    label = get_gap_label(gap['match_percentage'])

    return {
        "matched_skills": gap['matched_skills'],
        "missing_skills": gap['missing_skills'],
        "match_percentage": gap['match_percentage'],
        "gap_percentage": gap['gap_percentage'],
        "total_required": gap['total_required'],
        "total_matched": gap['total_matched'],
        "total_missing": gap['total_missing'],
        "suggestions": suggestions,
        "label": label
    }


# =============================================
# GEMINI AI FUNCTIONS
# =============================================

def get_ai_feedback(resume_data, jd_data, gap_result):
    try:
        prompt = (
            f"You are an expert HR recruiter.\n"
            f"Job: {jd_data['job_title']}\n"
            f"Candidate: {resume_data['name']}\n"
            f"Matched Skills: {', '.join(gap_result['matched_skills'])}\n"
            f"Missing Skills: {', '.join(gap_result['missing_skills'])}\n"
            f"Match: {gap_result['match_percentage']}%\n\n"
            f"Give:\n"
            f"1. Assessment (1 sentence)\n"
            f"2. Top 3 Strengths\n"
            f"3. Top 3 Improvements\n"
            f"4. Recommendation: Recommend/Maybe/Reject"
        )
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"AI feedback unavailable: {str(e)}"


def get_quick_summary(name, score, match_percentage, label):
    try:
        prompt = (
            f"Candidate {name} has {match_percentage}% skill match "
            f"and {score}% similarity score. "
            f"Write ONE sentence summary. Maximum 15 words only."
        )
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()

    except Exception as e:
        return f"Summary unavailable: {str(e)}"