import os
import time
from dotenv import load_dotenv
from resume_parser import parse_resume
from analyzer import (
    read_jd_from_file,
    calculate_similarity,
    full_gap_analysis,
    get_ai_feedback,
    get_quick_summary,
    get_similarity_label
)

# Load .env first
load_dotenv()

# Verify key loaded
key = os.getenv("GEMINI_API_KEY")
if not key:
    print("❌ API Key not found in .env file!")
    exit()
else:
    print(f"✅ API Key loaded: {key[:8]}...")

print("=" * 40)
print("GEMINI AI FEEDBACK TEST")
print("=" * 40)

# Load JD
jd = read_jd_from_file("sample_jd/jd1.txt")
print(f"JD: {jd['job_title']}")

# Test with 3 resumes only
test_resumes = [
    "resumes/resume01.pdf",
    "resumes/resume05.pdf",
    "resumes/resume10.pdf"
]

for i, resume_path in enumerate(test_resumes):
    print("\n" + "=" * 40)

    # Parse resume
    resume_data = parse_resume(resume_path)
    print(f"Analyzing: {resume_data['name']}")

    # Get similarity score
    score = calculate_similarity(
        resume_data['full_text'],
        jd['raw_text']
    )
    label = get_similarity_label(score)

    # Get skill gap
    gap = full_gap_analysis(resume_data, jd)

    # Get AI feedback
    print("Getting AI feedback...")
    feedback = get_ai_feedback(resume_data, jd, gap)

    # Wait before summary
    time.sleep(5)

    # Get quick summary
    print("Getting summary...")
    summary = get_quick_summary(
        resume_data['name'],
        score,
        gap['match_percentage'],
        gap['label']
    )

    # Print results
    print(f"\n👤 {resume_data['name']}")
    print(f"   Similarity  : {score}%  {label}")
    print(f"   Skill Match : {gap['match_percentage']}%  {gap['label']}")
    print(f"   ✅ Has      : {', '.join(gap['matched_skills'])}")
    print(f"   ❌ Missing  : {', '.join(gap['missing_skills'])}")
    print(f"\n💬 Quick Summary:")
    print(f"   {summary}")
    print(f"\n🤖 AI Feedback:")
    print(feedback)

    # Wait between resumes
    if i < len(test_resumes) - 1:
        print("\n⏳ Waiting 15 seconds...")
        time.sleep(15)

print("\n" + "=" * 40)
print("✅ Day 6 Complete!")
print("=" * 40)