from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from .resume_parser import extract_resume_data, match_resume_to_job

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Resume Analyzer API is live"}

@app.post("/analyze/")
async def analyze_resume(file: UploadFile = File(...)):
    temp_path = f"backend/uploads/{file.filename}"
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume_data = extract_resume_data(temp_path)
    job_description_skills = ["Python", "React.js", "AWS", "MySQL", "FastAPI"]
    match_score = match_resume_to_job(resume_data, job_description_skills)
    
    os.remove(temp_path)

    return {
        "resume_data": resume_data,
        "match_score": match_score
    }
