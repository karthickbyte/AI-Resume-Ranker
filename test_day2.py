from resume_parser import parse_resume
import os

# Test single resume
result = parse_resume("resumes/resume01.pdf")

print("=" * 40)
print("NAME:", result['name'])
print("EMAIL:", result['email'])
print("PHONE:", result['phone'])
print("=" * 40)
print("SKILLS:")
print(result['skills_section'])
print("EXPERIENCE:")
print(result['experience_section'])
print("EDUCATION:")
print(result['education_section'])

# Test all resumes
print("\n" + "=" * 40)
print("TESTING ALL RESUMES")
print("=" * 40)

resume_folder = "resumes"
all_resumes = os.listdir(resume_folder)

for resume_file in sorted(all_resumes):
    if resume_file.endswith('.pdf'):
        path = f"{resume_folder}/{resume_file}"
        result = parse_resume(path)
        print(f"\n📄 {resume_file}")
        print(f"   Name  : {result['name']}")
        print(f"   Email : {result['email']}")
        print(f"   Phone : {result['phone']}")
        print(f"   Skills: {result['skills_section'][:60].strip()}...")