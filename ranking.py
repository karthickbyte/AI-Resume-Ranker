import os
from resume_parser import parse_resume
from analyzer import (
    read_jd_from_file,
    calculate_similarity,
    full_gap_analysis,
    get_ai_feedback,
    get_quick_summary,
    get_similarity_label
)


def calculate_final_score(similarity_score, skill_match_percentage):
    # Weighted formula
    # 60% similarity + 40% skill match
    final_score = (
        (0.6 * similarity_score) +
        (0.4 * skill_match_percentage)
    )
    return round(final_score, 1)


def get_final_label(final_score):
    if final_score >= 80:
        return "🟢 Highly Recommended"
    elif final_score >= 60:
        return "🟡 Recommended"
    elif final_score >= 40:
        return "🟠 Maybe"
    else:
        return "🔴 Not Recommended"


def analyze_single_resume(resume_path, jd_data, candidate_name):
    try:
        # Step 1 - Read resume
        resume_data = parse_resume(resume_path)

        # Step 2 - Get similarity score
        similarity = calculate_similarity(
            resume_data['full_text'],
            jd_data['raw_text']
        )

        # Step 3 - Get skill gap
        gap = full_gap_analysis(resume_data, jd_data)

        # Step 4 - Calculate final score
        final_score = calculate_final_score(
            similarity,
            gap['match_percentage']
        )

        # Step 5 - Get final label
        label = get_final_label(final_score)

        return {
            "name": resume_data['name'],
            "file": candidate_name,
            "final_score": final_score,
            "similarity_score": similarity,
            "similarity_label": get_similarity_label(similarity),
            "skill_match": gap['match_percentage'],
            "matched_skills": gap['matched_skills'],
            "missing_skills": gap['missing_skills'],
            "suggestions": gap['suggestions'],
            "label": label,
            "resume_data": resume_data,
            "gap": gap
        }

    except Exception as e:
        return {
            "name": candidate_name,
            "file": candidate_name,
            "final_score": 0,
            "error": str(e)
        }


def rank_all_resumes(resume_folder, jd_data):
    all_results = []

    # Get all PDF files
    all_files = os.listdir(resume_folder)

    # Sort properly by number
    def sort_by_number(filename):
        numbers = ''.join(filter(str.isdigit, filename))
        return int(numbers) if numbers else 0

    sorted_files = sorted(all_files, key=sort_by_number)

    print(f"Found {len(sorted_files)} resumes to analyze...")
    print("=" * 40)

    for i, resume_file in enumerate(sorted_files):
        if resume_file.endswith('.pdf'):
            path = f"{resume_folder}/{resume_file}"
            print(f"Analyzing {i+1}/{len(sorted_files)}: {resume_file}")

            result = analyze_single_resume(
                path,
                jd_data,
                resume_file
            )
            all_results.append(result)

    # Sort by final score
    all_results.sort(
        key=lambda x: x['final_score'],
        reverse=True
    )

    # Add rank numbers
    for i, result in enumerate(all_results):
        result['rank'] = i + 1

    return all_results


def print_ranking_report(results, jd_data):
    print("\n" + "=" * 50)
    print(f"📋 JOB: {jd_data['job_title']}")
    print(f"🎯 Required Skills: {', '.join(jd_data['required_skills'])}")
    print("=" * 50)

    print("\n🏆 FINAL CANDIDATE RANKINGS")
    print("=" * 50)

    for r in results:
        print(f"\n#{r['rank']} {r['name']}")
        print(f"   Final Score    : {r['final_score']}%  {r['label']}")
        print(f"   Similarity     : {r['similarity_score']}%  {r['similarity_label']}")
        print(f"   Skill Match    : {r['skill_match']}%")
        print(f"   ✅ Has         : {', '.join(r['matched_skills']) if r['matched_skills'] else 'None'}")
        print(f"   ❌ Missing     : {', '.join(r['missing_skills']) if r['missing_skills'] else 'None'}")

    print("\n" + "=" * 50)
    print("🥇 TOP 3 CANDIDATES")
    print("=" * 50)

    for r in results[:3]:
        print(f"#{r['rank']} {r['name']} — {r['final_score']}% — {r['label']}")

    print("\n" + "=" * 50)
    print("❌ BOTTOM 3 CANDIDATES")
    print("=" * 50)

    for r in results[-3:]:
        print(f"#{r['rank']} {r['name']} — {r['final_score']}% — {r['label']}")