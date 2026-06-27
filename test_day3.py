from analyzer import read_jd_from_file, read_all_jds

print("=" * 40)
print("TESTING JD 1 - Python Developer")
print("=" * 40)

# Test single JD
jd = read_jd_from_file("sample_jd/jd1.txt")

print(f"Job Title  : {jd['job_title']}")
print(f"Experience : {jd['experience']}")
print(f"Total Skills Found: {jd['total_skills']}")
print(f"Required Skills:")
for skill in jd['required_skills']:
    print(f"  ✅ {skill}")

print("\n" + "=" * 40)
print("TESTING ALL 3 JDs")
print("=" * 40)

# Test all JDs
all_jds = read_all_jds("sample_jd")

for jd in all_jds:
    print(f"\n📋 {jd['filename']}")
    print(f"   Title     : {jd['job_title']}")
    print(f"   Experience: {jd['experience']}")
    print(f"   Skills    : {', '.join(jd['required_skills'])}")
    print(f"   Total     : {jd['total_skills']} skills found")