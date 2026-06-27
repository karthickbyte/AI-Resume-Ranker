from resume_parser import parse_resume
from analyzer import (
    read_jd_from_file,
    calculate_similarity,
    get_similarity_label
)
import os

print("=" * 40)
print("LOADING JD...")
print("=" * 40)

# Load JD 1 - Python Developer
jd = read_jd_from_file("sample_jd/jd1.txt")
print(f"JD Loaded: {jd['job_title']}")
print(f"Required Skills: {', '.join(jd['required_skills'])}")

print("\n" + "=" * 40)
print("TESTING SIMILARITY SCORES")
print("=" * 40)

# Test all resumes against JD1
resume_folder = "resumes"
all_resumes = os.listdir(resume_folder)

# Sort properly
def sort_by_number(filename):
    numbers = ''.join(filter(str.isdigit, filename))
    return int(numbers) if numbers else 0

sorted_resumes = sorted(all_resumes, key=sort_by_number)

results = []

for resume_file in sorted_resumes:
    if resume_file.endswith('.pdf'):
        path = f"{resume_folder}/{resume_file}"

        # Parse resume
        resume_data = parse_resume(path)

        # Calculate similarity
        score = calculate_similarity(
            resume_data['full_text'],
            jd['raw_text']
        )

        label = get_similarity_label(score)

        results.append({
            "file": resume_file,
            "name": resume_data['name'],
            "score": score,
            "label": label
        })

        print(f"📄 {resume_data['name']:<20} Score: {score}%  {label}")

# Sort by score
print("\n" + "=" * 40)
print("🏆 FINAL RANKING")
print("=" * 40)

results.sort(key=lambda x: x['score'], reverse=True)

for i, r in enumerate(results):
    print(f"#{i+1} {r['name']:<20} {r['score']}%  {r['label']}")