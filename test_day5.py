from resume_parser import parse_resume
from analyzer import read_jd_from_file, full_gap_analysis
import os

print("=" * 40)
print("SKILL GAP ANALYSIS")
print("=" * 40)

# Load JD
jd = read_jd_from_file("sample_jd/jd1.txt")
print(f"JD: {jd['job_title']}")
print(f"Required Skills: {', '.join(jd['required_skills'])}")

print("\n" + "=" * 40)
print("ANALYZING ALL RESUMES")
print("=" * 40)

# Sort resumes
resume_folder = "resumes"
all_resumes = os.listdir(resume_folder)

def sort_by_number(filename):
    numbers = ''.join(filter(str.isdigit, filename))
    return int(numbers) if numbers else 0

sorted_resumes = sorted(all_resumes, key=sort_by_number)

all_results = []

for resume_file in sorted_resumes:
    if resume_file.endswith('.pdf'):
        path = f"{resume_folder}/{resume_file}"

        # Parse resume
        resume_data = parse_resume(path)

        # Full gap analysis
        gap = full_gap_analysis(resume_data, jd)

        all_results.append({
            "name": resume_data['name'],
            "gap": gap
        })

        print(f"\n👤 {resume_data['name']}")
        print(f"   Match : {gap['match_percentage']}%  {gap['label']}")
        print(f"   ✅ Has : {', '.join(gap['matched_skills']) if gap['matched_skills'] else 'None'}")
        print(f"   ❌ Missing: {', '.join(gap['missing_skills']) if gap['missing_skills'] else 'None'}")

# Show learning suggestions for best candidate
print("\n" + "=" * 40)
print("📚 LEARNING SUGGESTIONS")
print("=" * 40)

for result in all_results:
    if result['gap']['missing_skills']:
        print(f"\n👤 {result['name']} should learn:")
        for skill, resource in result['gap']['suggestions'].items():
            print(f"   📖 {skill}: {resource}")

# Final ranking by skill match
print("\n" + "=" * 40)
print("🏆 FINAL RANKING BY SKILL MATCH")
print("=" * 40)

all_results.sort(
    key=lambda x: x['gap']['match_percentage'],
    reverse=True
)

for i, result in enumerate(all_results):
    gap = result['gap']
    print(f"#{i+1} {result['name']:<20} "
          f"Match: {gap['match_percentage']}% "
          f"✅{gap['total_matched']} "
          f"❌{gap['total_missing']}  "
          f"{gap['label']}")