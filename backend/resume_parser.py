import pdfplumber
import docx
import re
import spacy
from spacy.matcher import PhraseMatcher
from transformers import pipeline

# Load NLP Models
nlp = spacy.load("en_core_web_lg")
job_extractor = pipeline("ner", model="dslim/bert-base-NER")

# Skills Database (expandable)
SKILL_KEYWORDS = {"Python", "JavaScript", "PHP", "MySQL", "React.js", "Django", "FastAPI", "AWS", "Docker", "Git"}

# Job Titles Dataset
JOB_TITLES = [
    "Software Engineer", "Full-Stack Developer", "Backend Developer", "Frontend Developer",
    "Data Scientist", "Machine Learning Engineer", "AI Engineer", "Web Developer",
    "Project Manager", "System Analyst", "Product Manager", "DevOps Engineer"
]

# Degree Names Dataset (expandable)
DEGREES = [
    "B.Tech", "Bachelor of Science", "Master of Science", "M.Tech", "MBA",
    "PhD", "B.Sc", "M.Sc", "MCA", "B.E", "M.E", "BBA"
]

# Create a spaCy Matcher for job titles & degrees
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
job_patterns = [nlp.make_doc(title) for title in JOB_TITLES]
degree_patterns = [nlp.make_doc(degree) for degree in DEGREES]
matcher.add("JOB_TITLES", job_patterns)
matcher.add("DEGREES", degree_patterns)


def extract_text(file_path):
    """Extract text from PDF or DOCX and fix spacing issues."""
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return "Unsupported file format"

    # Fix word spacing using spaCy
    doc = nlp(text)
    clean_text = " ".join([token.text for token in doc])

    return clean_text


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF resume."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text.strip()


def extract_text_from_docx(docx_path):
    """Extract text from a DOCX resume."""
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()


def extract_skills(text):
    """Extract skills using AI-powered keyword matching."""
    found_skills = {skill for skill in SKILL_KEYWORDS if skill.lower() in text.lower()}
    return list(found_skills) if found_skills else ["No skills found"]


def extract_job_titles(text):
    """Extract job titles using spaCy PhraseMatcher."""
    doc = nlp(text)
    matches = matcher(doc)
    
    # Extract job titles only (ignore degrees)
    job_titles = [
        doc[start:end].text for match_id, start, end in matches 
        if matcher.vocab.strings[match_id] == "JOB_TITLES"
    ]
    
    # Filter out short/incorrect matches
    job_titles = [title for title in job_titles if len(title) > 3]

    return list(set(job_titles)) if job_titles else ["No job titles found"]


def extract_education(text):
    """Extract education details using regex + spaCy Matcher."""
    doc = nlp(text)
    matches = matcher(doc)
    
    # Extract degree names only (ignore job titles)
    degrees = [
        doc[start:end].text for match_id, start, end in matches 
        if matcher.vocab.strings[match_id] == "DEGREES"
    ]

    # Regex to catch common degree formats (e.g., "B.Tech in Computer Science")
    degree_pattern = r"(B\.?Tech|M\.?Tech|B\.?Sc|M\.?Sc|MBA|PhD|MCA|BBA|B\.?E|M\.?E)\s?(in\s[A-Za-z\s]+)?"
    regex_degrees = re.findall(degree_pattern, text)
    
    # Format regex matches properly
    regex_degrees = [" ".join(filter(None, degree)) for degree in regex_degrees]

    # Combine results from Matcher + Regex
    all_degrees = list(set(degrees + regex_degrees))

    return all_degrees if all_degrees else ["No education details found"]

def extract_resume_data(file_path):
    """Extract structured resume information."""
    text = extract_text(file_path)
    data = {
        "Skills": extract_skills(text),
        "Job Titles": extract_job_titles(text),
        "Education": extract_education(text),
    }
    return data


# Example Usage
if __name__ == "__main__":
    resume_data = extract_resume_data("C:/Users/Divya/Desktop/resume_analyzer/resume_analyzer/backend/sample_resume.docx")
    print("\nExtracted AI-Powered Resume Data:\n", resume_data)
