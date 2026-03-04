from flask import Flask, render_template, request
import os
import time
from resume_parser import extract_text_from_pdf, extract_text_from_docx
from model import calculate_similarity_score, calculate_ats_score

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():

    results = None
    error = None

    if request.method == "POST":

        job_desc = request.form.get("job_desc")
        files = request.files.getlist("resumes")

        if not job_desc or job_desc.strip() == "":
            return render_template("index.html", results=None, error="Please enter job description.")

        if not files or files[0].filename == "":
            return render_template("index.html", results=None, error="Please upload a resume file.")

        resume_texts = []
        filenames = []

        for file in files:

            if not allowed_file(file.filename):
                return render_template("index.html", results=None,
                                       error="Only PDF, DOCX, or JPG files allowed.")

            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            ext = file.filename.rsplit(".", 1)[1].lower()

            if ext == "pdf":
                text = extract_text_from_pdf(filepath)
            elif ext == "docx":
                text = extract_text_from_docx(filepath)
            elif ext in ["jpg", "jpeg", "png"]:
                # Image resume without OCR
                return render_template(
                    "index.html",
                    results=None,
                    error="Image resumes detected. OCR not enabled. Please upload text-based resume."
                )
            else:
                continue

            if not text or len(text.split()) < 100:
                return render_template(
                    "index.html",
                    results=None,
                    error="This file does not appear to be a valid resume."
                )

            # Stronger resume validation
            text_lower = text.lower()

            resume_sections = [
                "education",
                "experience",
                "skills",
                "projects",
                "certifications",
                "internship",
                "summary",
                "objective"
            ]

            section_count = sum(1 for section in resume_sections if section in text_lower)

            if section_count < 3:
                return render_template(
                    "index.html",
                    results=None,
                    error="Resume structure incomplete. Not a valid resume."
                )

            resume_texts.append(text)
            filenames.append(file.filename)

        time.sleep(3)

        results = []

        for i in range(len(resume_texts)):
            job_score = calculate_similarity_score(job_desc, resume_texts[i])
            ats_score = calculate_ats_score(resume_texts[i])

            results.append({
                "filename": filenames[i],
                "job_score": job_score,
                "ats_score": ats_score
            })

        results.sort(key=lambda x: x["job_score"], reverse=True)

    return render_template("index.html", results=results, error=error)


if __name__ == "__main__":
    app.run(debug=True)