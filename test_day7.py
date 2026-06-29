from analyzer import read_jd_from_file
from ranking import rank_all_resumes, print_ranking_report

print("=" * 50)
print("🤖 AI RESUME RANKER — COMPLETE SYSTEM")
print("=" * 50)

# Test with JD 1 — Python Developer
print("\n📋 Loading Job Description...")
jd = read_jd_from_file("sample_jd/jd1.txt")
print(f"✅ JD Loaded: {jd['job_title']}")
print(f"   Skills Required: {', '.join(jd['required_skills'])}")

# Rank all resumes
print("\n🔍 Analyzing all resumes...")
results = rank_all_resumes("resumes", jd)

# Print full report
print_ranking_report(results, jd)

# Summary statistics
print("\n" + "=" * 50)
print("📊 SUMMARY STATISTICS")
print("=" * 50)

total = len(results)
highly_recommended = len([r for r in results if r['final_score'] >= 80])
recommended = len([r for r in results if 60 <= r['final_score'] < 80])
maybe = len([r for r in results if 40 <= r['final_score'] < 60])
not_recommended = len([r for r in results if r['final_score'] < 40])

print(f"Total Candidates    : {total}")
print(f"🟢 Highly Recommended: {highly_recommended}")
print(f"🟡 Recommended       : {recommended}")
print(f"🟠 Maybe             : {maybe}")
print(f"🔴 Not Recommended   : {not_recommended}")

avg_score = sum(r['final_score'] for r in results) / total
print(f"📈 Average Score     : {round(avg_score, 1)}%")
print(f"🏆 Best Candidate    : {results[0]['name']} ({results[0]['final_score']}%)")
print(f"📉 Lowest Candidate  : {results[-1]['name']} ({results[-1]['final_score']}%)")