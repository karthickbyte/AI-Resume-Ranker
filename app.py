import streamlit as st
import pandas as pd
import os
import tempfile
from dotenv import load_dotenv
from analyzer import read_jd_from_file, parse_job_description
from resume_parser import parse_resume
from ranking import rank_all_resumes, analyze_single_resume

# =============================================
# LOGIN SYSTEM
# =============================================

# Valid credentials
USERS = {
    "admin": "admin123",
    "hr": "hr123",
    "recruiter": "recruit123"
}

def check_login(username, password):
    if username in USERS:
        if USERS[username] == password:
            return True
    return False

def show_login_page():
    st.title("🤖 AI Resume Ranker")
    st.subheader("Please login to continue")
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 🔐 Login")

        username = st.text_input(
            "Username",
            placeholder="Enter username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
            key="login_password"
        )

        login_btn = st.button(
            "Login",
            type="primary",
            use_container_width=True
        )

        if login_btn:
            if check_login(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error("❌ Wrong username or password!")

        st.divider()
        st.markdown("**Demo Credentials:**")
        st.info("""
        Username: admin  Password: admin123
        Username: hr     Password: hr123
        """)

# =============================================
# CHECK LOGIN STATUS
# =============================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    show_login_page()
    st.stop()

# =============================================
# SHOW LOGOUT IN SIDEBAR
# =============================================
with st.sidebar:
    st.markdown(f"👤 Logged in as: **{st.session_state['username']}**")
    if st.button("🚪 Logout"):
        st.session_state['logged_in'] = False
        st.rerun()
    st.divider()
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
    st.title("About This App")
    st.markdown("""
    This AI tool helps HR recruiters:
    - 📄 Read and parse resumes
    - 🎯 Match candidates to JD
    - 📊 Rank candidates by score
    - ❌ Find skill gaps
    - 📚 Suggest learning resources
    """)
    st.divider()

    st.markdown("**How to Use:**")
    st.markdown("1. Add Job Description")
    st.markdown("2. Upload PDF Resumes")
    st.markdown("3. Click Analyze button")
    st.markdown("4. See ranked results!")
    st.divider()

    st.markdown("**Built by:**")
    st.markdown("Karthick J")
    st.markdown("AI-Powered Resume Ranker")
# =============================================
# MAIN CONTENT
# =============================================

# Two column layout
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("📋 Job Description")

    # Pre-loaded JD templates
    jd_templates = {
        "Select a Template": "",
        "Python Developer": """Job Title: Python Developer
Company: Tech Solutions Pvt Ltd

Required Skills:
- Python
- SQL
- Machine Learning
- Communication
- Problem Solving

Experience: 0-2 years
Education: B.Tech Computer Science""",

        "Data Analyst": """Job Title: Data Analyst
Company: Analytics Corp

Required Skills:
- Python
- Excel
- Power BI
- SQL
- Data Visualization
- Communication

Experience: 0-2 years
Education: B.Tech / BCA / B.Sc""",

        "Machine Learning Engineer": """Job Title: Machine Learning Engineer
Company: AI Ventures

Required Skills:
- Python
- Machine Learning
- Deep Learning
- NLP
- TensorFlow
- SQL
- Git

Experience: 1-2 years
Education: B.Tech Computer Science""",

        "Full Stack Developer": """Job Title: Full Stack Developer
Company: Web Solutions

Required Skills:
- Python
- Django
- React
- SQL
- HTML
- CSS
- Git

Experience: 0-2 years
Education: B.Tech Computer Science""",

        "Data Scientist": """Job Title: Data Scientist
Company: Data Corp

Required Skills:
- Python
- Machine Learning
- Statistics
- SQL
- Deep Learning
- Communication

Experience: 1-2 years
Education: B.Tech Computer Science"""
    }

    jd_input_method = st.radio(
        "How to add JD?",
        ["Use Template", "Type or Paste", "Upload Text File"],
        horizontal=True
    )

    jd_text = ""

    if jd_input_method == "Use Template":
        selected_template = st.selectbox(
            "Select Job Role Template",
            list(jd_templates.keys())
        )

        if selected_template != "Select a Template":
            # Single text area with template loaded
            jd_text = st.text_area(
                "JD loaded — edit if needed:",
                value=jd_templates[selected_template],
                height=250,
                key="template_box"
            )
            st.success(f"✅ Template loaded: {selected_template}")
        else:
            st.info("👆 Please select a job role")
            jd_text = ""

    elif jd_input_method == "Type or Paste":
        # Single text area only
        jd_text = st.text_area(
            "Paste Job Description here",
            height=250,
            key="paste_box",
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
            type=['txt'],
            key="jd_uploader"
        )
        if jd_file:
            jd_text = jd_file.read().decode('utf-8')
            st.success("✅ JD file uploaded!")
            st.text_area(
                "JD Content:",
                jd_text,
                height=200,
                key="upload_box"
            )


# Right column - Resume Upload
with col2:
    st.subheader("📄 Upload Resumes")

    uploaded_resumes = st.file_uploader(
        "Upload PDF resumes (multiple allowed)",
        type=['pdf'],
        accept_multiple_files=True,
        key="resume_uploader"
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
        # CHARTS SECTION
        # =============================================
        st.subheader("📈 Score Comparison Chart")

        import plotly.express as px
        import plotly.graph_objects as go

        # Bar chart data
        chart_data = pd.DataFrame({
            'Candidate': [r['name'] for r in results],
            'Final Score': [r['final_score'] for r in results],
            'Skill Match': [r['skill_match'] for r in results],
            'Similarity': [r['similarity_score'] for r in results]
        })

        # Bar chart
        fig = px.bar(
            chart_data,
            x='Candidate',
            y=['Final Score', 'Skill Match', 'Similarity'],
            barmode='group',
            title='Candidate Score Comparison',
            color_discrete_sequence=['#2196F3', '#4CAF50', '#FF9800']
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # =============================================
        # SKILL GAP CHART
        # =============================================
        st.subheader("🎯 Skill Match Overview")

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            # Pie chart for recommendations
            rec_counts = {
                "Highly Recommended": len([r for r in results if r['final_score'] >= 80]),
                "Recommended": len([r for r in results if 60 <= r['final_score'] < 80]),
                "Maybe": len([r for r in results if 40 <= r['final_score'] < 60]),
                "Not Recommended": len([r for r in results if r['final_score'] < 40])
            }

            fig_pie = px.pie(
                values=list(rec_counts.values()),
                names=list(rec_counts.keys()),
                title='Candidate Distribution',
                color_discrete_sequence=[
                    '#4CAF50', '#2196F3', '#FF9800', '#F44336'
                ]
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_chart2:
            # Horizontal bar for final scores
            fig_bar = px.bar(
                chart_data.sort_values('Final Score'),
                x='Final Score',
                y='Candidate',
                orientation='h',
                title='Final Score Ranking',
                color='Final Score',
                color_continuous_scale='RdYlGn'
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # =============================================
        # SUMMARY STATISTICS
        # =============================================
        st.subheader("📊 Summary Statistics")

        total = len(results)
        avg_score = sum(r['final_score'] for r in results) / total
        highest = results[0]
        lowest = results[-1]

        stat1, stat2, stat3, stat4 = st.columns(4)

        stat1.metric(
            "Total Candidates",
            total
        )
        stat2.metric(
            "Average Score",
            f"{round(avg_score, 1)}%"
        )
        stat3.metric(
            "Best Score",
            f"{highest['final_score']}%",
            f"{highest['name']}"
        )
        stat4.metric(
            "Lowest Score",
            f"{lowest['final_score']}%",
            f"{lowest['name']}"
        )

        st.divider()

        # =============================================
        # SKILL GAP TABLE
        # =============================================
        st.subheader("🔍 Skill Gap Analysis")

        # Show skills heatmap
        all_skills = jd_data['required_skills']
        skill_data = []

        for r in results:
            row = {'Candidate': r['name']}
            for skill in all_skills:
                if skill in r['matched_skills']:
                    row[skill] = '✅'
                else:
                    row[skill] = '❌'
            skill_data.append(row)

        skill_df = pd.DataFrame(skill_data)
        st.dataframe(skill_df, use_container_width=True)

        st.divider()

        # =============================================
        # LEARNING SUGGESTIONS
        # =============================================
        st.subheader("📚 Learning Recommendations")

        for r in results:
            if r['missing_skills']:
                with st.expander(
                    f"📖 {r['name']} — {len(r['missing_skills'])} skills to learn"
                ):
                    for skill, resource in r['suggestions'].items():
                        st.write(f"**{skill}:** {resource}")

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