import React, { useState } from 'react';
import './App.css';

const JOB_OPTIONS = [
  { label: "Frontend Developer", skills: ["React.js", "JavaScript", "HTML", "CSS"] },
  { label: "Backend Developer", skills: ["Python", "FastAPI", "Django", "MySQL"] },
  { label: "Full-Stack Developer", skills: ["React.js", "FastAPI", "Git", "Docker"] },
  { label: "Data Scientist", skills: ["Python", "Pandas", "NumPy", "Scikit-learn"] }
];

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [job, setJob] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
  };

  const handleUpload = async () => {
    if (!file || !job) return alert("Please select both a resume file and a job role.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);

      const res = await fetch("http://127.0.0.1:8000/analyze/", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Error uploading file:", err);
      alert("Failed to analyze. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App d-flex justify-content-center align-items-center bg-dark text-light min-vh-100">
      <link
        rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
        integrity="sha384-ENjdO4Dr2bkBIFxQpeoQc9gyP6Y9H9vvZ7e0x0A5GvUjFa57IwtOJFOa8hPYyYZ0"
        crossOrigin="anonymous"
      />

      <div className="container" style={{ maxWidth: '600px', width: '100%' }}>
        <h1 className="text-center text-primary mb-4">Resume Analyzer</h1>

        <form className="bg-dark border border-secondary rounded p-4 shadow">
          <div className="mb-3">
            <label className="form-label">Upload Resume:</label>
            <input type="file" className="form-control" onChange={handleFileChange} />
          </div>

          <div className="mb-3">
            <label className="form-label">Select Job Role:</label>
            <select className="form-select" onChange={(e) => setJob(JOB_OPTIONS[e.target.value])} defaultValue="">
              <option value="" disabled>Select a role</option>
              {JOB_OPTIONS.map((role, index) => (
                <option key={index} value={index}>{role.label}</option>
              ))}
            </select>
          </div>

          <div className="d-grid">
            <button className="btn btn-primary" type="button" onClick={handleUpload} disabled={loading}>
              {loading ? "Analyzing..." : "Analyze Resume"}
            </button>
          </div>
        </form>

        {result && (
          <div className="results bg-secondary p-4 rounded mt-5">
            <h2 className="text-info">Extracted Resume Data</h2>
            <p><strong>Skills:</strong> {result.resume_data.Skills.join(", ")}</p>
            <p><strong>Job Titles:</strong> {result.resume_data["Job Titles"].join(", ")}</p>
            <p><strong>Education:</strong> {result.resume_data.Education.join(", ")}</p>

            <h2 className="text-info mt-4">Matching Score</h2>
            <p><strong>{job?.label}</strong>: {(result.match_score["Matching Score"] * 100).toFixed(2)}%</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
