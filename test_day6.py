from google import genai
from resume_parser import parse_resume
from analyzer import (
    read_jd_from_file,
    calculate_similarity,
    full_gap_analysis,
    get_similarity_label
)
import time

# ✅ Direct API key here
GEMINI_API_KEY = "AQ.Ab8RN6Iw0Gbo9JjalGyTS9p-kofkR40NdqvcE0i9vfUvduFZ7w"

gemini_client = genai.Client(api_key=GEMINI_API_KEY)


def get_ai_feedback(resume_data, jd_data, gap_result):
    try:
        prompt = (
            f"You are an HR recruiter.\n"
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


def get_quick_summary(name, score, match_percentage):
    try:
        prompt = (
            f"Candidate {name} has {match_percentage}% skill match "
            f"and {score}% similarity. "
            f"Write ONE sentence. Maximum 15 words only."
        )

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()

    except Exception as e:
        return f"Summary unavailable: {str(e)}"


# =============================================
print("=" * 40)
print("GEMINI AI FEEDBACK TEST")
print("=" * 40)

# Test API first
print("\n🔍 Testing API connection...")
try:
    test_response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say OK"
    )
    print(f"✅ API Connected! Response: {test_response.text.strip()}")
except Exception as e:
    print(f"❌ API Failed: {e}")
    exit()

# Load JD
print("\n📋 Loading Job Description...")
jd = read_jd_from_file("sample_jd/jd1.txt")
print(f"✅ JD Loaded: {jd['job_title']}")
print(f"   Skills: {', '.join(jd['required_skills'])}")

# Test with 2 resumes only
test_resumes = [
    "resumes/resume01.pdf",
    "resumes/resume05.pdf"
]

for i, resume_path in enumerate(test_resumes):
    print("\n" + "=" * 40)

    # Parse resume
    resume_data = parse_resume(resume_path)
    print(f"📄 Analyzing: {resume_data['name']}")

    # Similarity score
    score = calculate_similarity(
        resume_data['full_text'],
        jd['raw_text']
    )
    label = get_similarity_label(score)

    # Skill gap
    gap = full_gap_analysis(resume_data, jd)

    # AI Feedback
    print("🤖 Getting AI feedback...")
    feedback = get_ai_feedback(resume_data, jd, gap)

    # Wait before next API call
    time.sleep(5)

    # Quick summary
    print("💬 Getting summary...")
    summary = get_quick_summary(
        resume_data['name'],
        score,
        gap['match_percentage']
    )

    # Print all results
    print(f"\n{'=' * 40}")
    print(f"👤 {resume_data['name']}")
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