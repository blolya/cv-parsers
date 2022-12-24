import os
import glob
import json
import pandas as pd
from pathlib import Path
from affinda import AffindaAPI, TokenCredential

token = os.environ['AFFINDA_TOKEN']
credential = TokenCredential(token=token)
client = AffindaAPI(credential=credential)

input_dir = os.environ['INPUT_DIR']
output_dir = os.environ['OUTPUT_DIR'] + "/affinda"

input_files = []
exts = ["*.pdf", "*.docx"]
for ext in exts:
    input_files.append( glob.glob(os.path.join(input_dir, ext)) )

input_files = [item for sublist in input_files for item in sublist]
resumes = []
for input_file in input_files:
    print(input_file)
    input_path = Path(input_file)

    with open(input_path, "rb") as f:
        resume_raw = client.create_resume(file=f)

    resume = resume_raw.as_dict()
    output_file = os.path.join(output_dir, input_path.stem + ".json")
    with open(output_file, "w") as f:
        f.write(json.dumps(resume))

    resumes.append(resume)    

rows_list = []
for resume in resumes:
    print(resume)
    data = resume.get("data")

    name = data.get("name").get("raw")
    date_of_birth = data.get("date_of_birth")
    
    location = data.get("location").get("raw_input") if data.get("location") else ""
    phones = "; ".join(data.get("phone_numbers"))
    emails = "; ".join(data.get("emails"))
    websites = "; ".join(data.get("websites"))

    summary = data.get("summary")

    languages = "; ".join(data.get("languages"))

    def create_education(e):
        return ", ".join([
            "date: " + e.get("dates").get("completion_date") if e.get("dates") else "",
            "organization: " + e.get("organization"), 
            "accreditation: " + e.get("accreditation").get("education")
        ])
    education = "; ".join( map(create_education, data.get("education")) )

    profession = data.get("profession")

    def create_work_experience(we):
        return ", ".join([
            "dates: " + we.get("dates").get("start_date") + "/" + we.get("dates").get("end_date"),
            "organization: " + we.get("organization"),
            "job title: " + we.get("job_title"),
            "job description: " + we.get("job_description")
        ])
    work_experience = "; ".join( map(create_work_experience, data.get("work_experience")) )

    skills = "; ".join( map(lambda s: s.get("name"), data.get("skills")) )

    rows_list.append({
        "name": name, "date_of_birth": date_of_birth, "location": location, "phones": phones,
        "emails": emails, "websites": websites, "summary": summary,
        "languages": languages, "education": education, "profession": profession,
        "work_experience": work_experience, "skills": skills
    })

columns = ["name", "date_of_birth", "location", "phones",
           "emails", "websites", "summary",
           "languages", "education", "profession", 
           "work_experience", "skills"]
df = pd.DataFrame(rows_list, columns = columns)

df.to_excel(output_dir + "/resumes.xlsx")