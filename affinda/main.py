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

# Read file names from input dir and filter by extensions
input_files = glob.glob(input_dir + "/*")
exts = [".pdf", ".docx"]
input_files = list( filter(lambda f: Path(f).suffix in exts, input_files) ) \
    if len(exts) > 0 \
    else input_files

resumes = []
for input_file in input_files:
    print(f"Parsing: {input_file}")

    input_path = Path(input_file)

    with open(input_path, "rb") as f:
        raw_resume = client.create_resume(file=f)

    resume = raw_resume.as_dict()

    output_file = os.path.join(output_dir, f"{input_path.stem}.json")
    with open(output_file, "w") as f:
        f.write(json.dumps(resume))

    resume["file"] = input_file
    resumes.append(resume)    

rows_list = []
for resume in resumes:
    data = resume.get("data", {})

    name = data.get("name", {}).get("raw", "No name")
    date_of_birth = data.get("date_of_birth", "No date of birth")
    
    location = data.get("location", {}).get("raw_input", "No address")
    phones = "; ".join( data.get("phone_numbers", ["No phone"]) ) 
    emails = "; ".join( data.get("emails", ["No email"]) )
    websites = "; ".join( data.get("websites", ["No website"]) )

    summary = data.get("summary", "No summary")

    languages = "; ".join( data.get("languages", "No languages") )

    def create_education(e):
        completion_date = e.get("dates", {}).get("completion_date", "No completion date") 
        organization = e.get("organization", "No organization")
        education = e.get("accreditation", {}).get("education", "No accreditation")
        return ", ".join([
            f"date: {completion_date}",
            f"organization: {organization}", 
            f"accreditation: {education}"
        ])
    education = "; ".join( map(create_education, data.get("education", [])) )

    profession = data.get("profession", "No profession")

    def create_work_experience(we):
        dates = we.get("dates", {})
        start_date = dates.get("start_date", "No start date")
        end_date = dates.get("end_date", "No end date")

        organization = we.get("organization", "No organization")
        job_title = we.get("job_title", "No job title")
        job_description = we.get("job_description", "No job description")

        return ", ".join([
            f"dates: {start_date}/{end_date}",
            f"organization: {organization}",
            f"job title: {job_title}",
            f"job description: {job_description}"
        ])
    work_experience = "; ".join( map(create_work_experience, data.get("work_experience", [])) )

    skills = "; ".join( map(lambda s: s.get("name"), data["skills"]) ) if "skills" in data else "No skills"

    rows_list.append({
        "name": name, "date_of_birth": date_of_birth, "location": location, "phones": phones,
        "emails": emails, "websites": websites, "summary": summary,
        "languages": languages, "education": education, "profession": profession,
        "work_experience": work_experience, "skills": skills, "file": resume["file"]
    })

df = pd.DataFrame(rows_list)

df.to_excel(output_dir + "/resumes.xlsx")