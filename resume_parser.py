import pdfplumber
import re

def extract_text_from_pdf(pdf_path):
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

        if len(full_text.strip()) < 50:
            return "Could not extract text. PDF may be image based."

    except Exception as e:
        return f"Error reading PDF: {str(e)}"

    return full_text


def extract_name(text):
    # Look for "Name:" pattern
    for line in text.split('\n'):
        line = line.strip()
        if line.lower().startswith('name:'):
            return line.split(':', 1)[1].strip()
    return "Unknown"


def extract_email(text):
    # Look for "Email:" pattern first
    for line in text.split('\n'):
        line = line.strip()
        if line.lower().startswith('email:'):
            return line.split(':', 1)[1].strip()
    
    # Fallback to regex
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not found"


def extract_phone(text):
    # Look for "Phone:" pattern first
    for line in text.split('\n'):
        line = line.strip()
        if line.lower().startswith('phone:'):
            return line.split(':', 1)[1].strip()
    
    # Fallback to regex
    phone_pattern = r'\b[6-9]\d{9}\b'
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else "Not found"


def extract_sections(text):
    sections = {
        "skills": "",
        "experience": "",
        "education": "",
        "objective": "",
        "certifications": ""
    }

    current_section = None
    lines = text.split('\n')

    for line in lines:
        line_lower = line.lower().strip()

        # Detect section headers
        if line_lower.startswith('skill'):
            current_section = 'skills'
        elif line_lower.startswith('experience') or line_lower.startswith('work'):
            current_section = 'experience'
        elif line_lower.startswith('education'):
            current_section = 'education'
        elif line_lower.startswith('objective') or line_lower.startswith('summary'):
            current_section = 'objective'
        elif line_lower.startswith('certif'):
            current_section = 'certifications'
        elif current_section:
            sections[current_section] += line + "\n"

    return sections


def parse_resume(pdf_path):
    # Step 1 - Extract full text
    full_text = extract_text_from_pdf(pdf_path)

    # Step 2 - Extract sections
    sections = extract_sections(full_text)

    # Step 3 - Extract details
    name = extract_name(full_text)
    email = extract_email(full_text)
    phone = extract_phone(full_text)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "full_text": full_text,
        "skills_section": sections['skills'],
        "experience_section": sections['experience'],
        "education_section": sections['education'],
        "certifications_section": sections['certifications']
    }