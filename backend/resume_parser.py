import re
import docx
import pdfplumber
import spacy
from spacy.matcher import PhraseMatcher
from transformers import pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_lg")
job_extractor = pipeline("ner", model="dslim/bert-base-NER")

SKILL_KEYWORDS = {"Python", "JavaScript", "PHP", "MySQL", "React.js", "Django", "FastAPI", "AWS", "Docker", "Git"}
JOB_TITLES = [
    "Software Engineer", "Full-Stack Developer", "Backend Developer", "Frontend Developer",
    "Data Scientist", "Machine Learning Engineer", "AI Engineer", "Web Developer",
    "Project Manager", "System Analyst", "Product Manager", "DevOps Engineer"
]
DEGREES = ["B.Tech", "Bachelor of Science", "Master of Science", "M.Tech", "MBA", "PhD", "B.Sc", "M.Sc", "MCA", "B.E", "M.E", "BBA"]

def create_phrase_matcher():
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    job_patterns = [nlp.make_doc(title) for title in JOB_TITLES]
    degree_patterns = [nlp.make_doc(degree) for degree in DEGREES]
    matcher.add("JOB_TITLES", job_patterns)
    matcher.add("DEGREES", degree_patterns)
    return matcher

matcher = create_phrase_matcher()

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        return ""

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
    except Exception as e:
        print("PDF error:", e)
    return text.strip()

def extract_text_from_docx(docx_path):
    text = ""
    try:
        doc = docx.Document(docx_path)
        text = "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        print("DOCX error:", e)
    return text.strip()

def extract_skills(text):
    return [skill for skill in SKILL_KEYWORDS if skill.lower() in text.lower()] or ["No skills found"]

def extract_job_titles(text):
    doc = nlp(text)
    matches = matcher(doc)
    return list(set(doc[start:end].text for match_id, start, end in matches if matcher.vocab.strings[match_id] == "JOB_TITLES")) or ["No job titles found"]

def extract_education(text):
    doc = nlp(text)
    matches = matcher(doc)
    degrees = [doc[start:end].text for match_id, start, end in matches if matcher.vocab.strings[match_id] == "DEGREES"]
    degree_pattern = r"(B\.?Tech|M\.?Tech|B\.?Sc|M\.?Sc|MBA|PhD|MCA|BBA|B\.?E|M\.?E)\s?(in\s[A-Za-z\s]+)?"
    regex_degrees = [" ".join(filter(None, match)) for match in re.findall(degree_pattern, text)]
    return list(set(degrees + regex_degrees)) or ["No education details found"]

def extract_entities_bert(text):
    entities = job_extractor(text)
    output = {"PER": set(), "ORG": set(), "LOC": set(), "MISC": set()}
    
    for ent in entities:
        label = ent['entity'].replace("B-", "").replace("I-", "")
        if label in output:
            output[label].add(ent['word'])
    
    return {k: list(v) for k, v in output.items()}


def calculate_similarity(resume_skills, job_skills):
    if not resume_skills or not job_skills or resume_skills == ["No skills found"]:
        return 0.0
    texts = [' '.join(resume_skills), ' '.join(job_skills)]
    vectorizer = CountVectorizer().fit_transform(texts)
    if vectorizer.shape[0] < 2:
        return 0.0
    cosine_sim = cosine_similarity(vectorizer)
    return float(cosine_sim[0][1])

def extract_resume_data(file_path):
    raw_text = extract_text(file_path)
    clean_text = " ".join([token.text for token in nlp(raw_text)])

    return {
        "Skills": extract_skills(clean_text),
        "Job Titles": extract_job_titles(clean_text),
        "Education": extract_education(clean_text)
        # ,"Entities (BERT)": extract_entities_bert(clean_text)
    }


def match_resume_to_job(resume_data, job_description_skills):
    return {"Matching Score": calculate_similarity(resume_data["Skills"], job_description_skills)}

if __name__ == "__main__":
    resume_path = "C:/Users/Divya/Desktop/resume_analyzer/resume_analyzer/backend/sample_resume.docx"
    job_description_skills = ["Python", "React.js", "AWS", "MySQL", "FastAPI"]
    
    resume_data = extract_resume_data(resume_path)
    match_score = match_resume_to_job(resume_data, job_description_skills)

    print("\nExtracted Resume Data:\n", resume_data)
    print("\nMatching Score:\n", match_score)
