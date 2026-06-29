import streamlit as st
import pandas as pd
import os
import tempfile
from dotenv import load_dotenv
from analyzer import read_jd_from_file, parse_job_description
from resume_parser import parse_resume
from ranking import rank_all_resumes, analyze_single_resume

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Resume Ranker",
    page_icon="🤖",
    layout="wide"
)

# Title section
st.title("🤖 AI-Powered Resume Ranker & Skill Gap Analyzer")
st.markdown("**Upload a Job Description and resumes to find the best candidates instantly!**")
st.divider()

# =============================================
# SIDEBAR
# =============================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png")
    st.title("About This App")
    st.markdown("""
    This AI tool helps HR recruiters:
    - 📄 Read and parse resumes
    - 🎯 Match candidates to job descriptions
    - 📊 Rank candidates by fit score
    - ❌ Find skill gaps
    - 📚 Suggest learning resources
    - 🤖 Get AI powered feedback
    """)
    st.divider()
    st.markdown("**Built with:**")
    st.markdown("- Python")
    st.markdown("- Streamlit")
    st.markdown("- Gemini AI")
    st.markdown("- Sentence Transformers")

# =============================================
# MAIN CONTENT
# =============================================

# Two column layout
col1, col2 = st.columns([1, 1])

# Left column - JD Input
with col1:
    st.subheader("📋 Job Description")

    jd_input_method = st.radio(
        "How to add JD?",
        ["Type or Paste", "Upload Text File"],
        horizontal=True
    )

    jd_text = ""

    if jd_input_method == "Type or Paste":
        jd_text = st.text_area(
            "Paste Job Description here",
            height=250,
            placeholder="""Job Title: Python Developer
Required Skills:
- Python
- SQL
- Machine Learning
- Communication
Experience: 0-2 years"""
        )

    else:
        jd_file = st.file_uploader(
            "Upload JD (.txt file)",
            type=['txt']
        )
        if jd_file:
            jd_text = jd_file.read().decode('utf-8')
            st.success("✅ JD file uploaded!")
            st.text_area(
                "JD Content:",
                jd_text,
                height=200
            )

# Right column - Resume Upload
with col2:
    st.subheader("📄 Upload Resumes")

    uploaded_resumes = st.file_uploader(
        "Upload PDF resumes (multiple allowed)",
        type=['pdf'],
        accept_multiple_files=True
    )

    if uploaded_resumes:
        st.success(f"✅ {len(uploaded_resumes)} resume(s) uploaded!")
        for resume in uploaded_resumes:
            st.write(f"📄 {resume.name}")
    else:
        st.info("👆 Upload one or more PDF resumes")

st.divider()

# =============================================
# ANALYZE BUTTON
# =============================================

analyze_btn = st.button(
    "🚀 Analyze Resumes",
    type="primary",
    use_container_width=True
)

# =============================================
# ANALYSIS RESULTS
# =============================================

if analyze_btn:
    # Validation
    if not jd_text:
        st.error("❌ Please add a Job Description first!")

    elif not uploaded_resumes:
        st.error("❌ Please upload at least one resume!")

    else:
        # Show progress
        with st.spinner("🤖 AI is analyzing resumes... please wait!"):

            # Parse JD
            jd_data = parse_job_description(jd_text)

            # Save uploaded resumes temporarily
            temp_dir = tempfile.mkdtemp()
            results = []

            progress = st.progress(0)
            total = len(uploaded_resumes)

            for i, resume_file in enumerate(uploaded_resumes):
                # Save temp file
                temp_path = os.path.join(
                    temp_dir,
                    resume_file.name
                )
                with open(temp_path, 'wb') as f:
                    f.write(resume_file.read())

                # Analyze resume
                result = analyze_single_resume(
                    temp_path,
                    jd_data,
                    resume_file.name
                )
                results.append(result)

                # Update progress
                progress.progress((i + 1) / total)

            # Sort by final score
            results.sort(
                key=lambda x: x['final_score'],
                reverse=True
            )

            # Add ranks
            for i, r in enumerate(results):
                r['rank'] = i + 1

        st.success("✅ Analysis Complete!")
        st.balloons()

        # =============================================
        # SHOW JD DETAILS
        # =============================================
        st.subheader("📋 Job Description Analysis")
        col_a, col_b = st.columns(2)

        with col_a:
            st.metric("Job Title", jd_data['job_title'])
            st.metric("Total Skills Required", jd_data['total_skills'])

        with col_b:
            st.write("**Required Skills:**")
            skills_text = " • ".join(jd_data['required_skills'])
            st.info(skills_text)

        st.divider()

        # =============================================
        # RANKING TABLE
        # =============================================
        st.subheader("🏆 Candidate Rankings")

        table_data = []
        for r in results:
            table_data.append({
                "Rank": f"#{r['rank']}",
                "Candidate": r['name'],
                "Final Score": f"{r['final_score']}%",
                "Similarity": f"{r['similarity_score']}%",
                "Skill Match": f"{r['skill_match']}%",
                "Matched": len(r['matched_skills']),
                "Missing": len(r['missing_skills']),
                "Recommendation": r['label']
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)

        st.divider()

        # =============================================
        # BEST CANDIDATE HIGHLIGHT
        # =============================================
        best = results[0]
        st.success(f"🏆 Best Candidate: **{best['name']}** with score **{best['final_score']}%**")

        st.divider()

        # =============================================
        # INDIVIDUAL CANDIDATE CARDS
        # =============================================
        st.subheader("📊 Detailed Analysis")

        for r in results:
            with st.expander(
                f"#{r['rank']} {r['name']} — {r['final_score']}% — {r['label']}"
            ):
                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Final Score", f"{r['final_score']}%")
                m2.metric("Similarity", f"{r['similarity_score']}%")
                m3.metric("Skill Match", f"{r['skill_match']}%")

                # Skills
                c1, c2 = st.columns(2)
                with c1:
                    st.write("✅ **Matched Skills**")
                    if r['matched_skills']:
                        for skill in r['matched_skills']:
                            st.write(f"  • {skill}")
                    else:
                        st.write("None")

                with c2:
                    st.write("❌ **Missing Skills**")
                    if r['missing_skills']:
                        for skill in r['missing_skills']:
                            st.write(f"  • {skill}")
                    else:
                        st.write("None — Perfect Match!")

                # Learning suggestions
                if r['suggestions']:
                    st.write("📚 **Learning Suggestions**")
                    for skill, resource in r['suggestions'].items():
                        st.write(f"  • **{skill}:** {resource}")

        st.divider()

        # =============================================
        # DOWNLOAD RESULTS
        # =============================================
        st.subheader("⬇️ Download Results")

        csv_data = pd.DataFrame([{
            'Rank': r['rank'],
            'Name': r['name'],
            'Final Score': r['final_score'],
            'Similarity Score': r['similarity_score'],
            'Skill Match': r['skill_match'],
            'Matched Skills': ', '.join(r['matched_skills']),
            'Missing Skills': ', '.join(r['missing_skills']),
            'Recommendation': r['label']
        } for r in results])

        st.download_button(
            label="⬇️ Download Results as CSV",
            data=csv_data.to_csv(index=False),
            file_name="resume_rankings.csv",
            mime="text/csv",
            use_container_width=True
        )