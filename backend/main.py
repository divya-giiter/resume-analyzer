from fastapi import FastAPI, File, UploadFile
import shutil
# from resume_parser import extract_resume_data
from .resume_parser import extract_resume_data

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the Resume Analyzer API woza"}

@app.post("/upload/")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a resume file (PDF or DOCX) and extract structured data."""
    file_path = f"backend/uploads/{file.filename}"
    
    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Extract structured resume data
    extracted_data = extract_resume_data(file_path)
    
    return {"filename": file.filename, "resume_data": extracted_data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
