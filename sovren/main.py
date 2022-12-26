import base64
import requests
import json
import os.path
import datetime
import glob
import pandas as pd
from pathlib import Path

account_id = os.environ['SOVREN_ACCOUNT_ID']
token = os.environ['SOVREN_TOKEN']

input_dir = os.environ['INPUT_DIR']
output_dir = os.environ['OUTPUT_DIR'] + "/sovren"

input_files = glob.glob(input_dir + "/*")
exts = [".pdf", ".docx"]
input_files = list( filter(lambda f: Path(f).suffix in exts, input_files) ) \
    if len(exts) > 0 \
    else input_files
 
def parse_resume(file, account_id, token):
    base64str = ''
    with open(input_file, 'rb') as f:
        base64str = base64.b64encode(f.read()).decode('UTF-8')
 
    epoch_seconds = os.path.getmtime(file)
    last_modified_date = datetime.datetime.fromtimestamp(epoch_seconds).strftime("%Y-%m-%d") 
 
    url = "https://eu-rest.resumeparsing.com/v10/parser/resume"
    payload = {
      'DocumentAsBase64String': base64str,
      'DocumentLastModified': last_modified_date
    }
     
    headers = {
      'accept': "application/json",
      'content-type': "application/json",
      'sovren-accountid': account_id,
      'sovren-servicekey': token,
    }
     
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    return response.content

resumes = []
for input_file in input_files:
    json_resume = parse_resume(input_file, account_id, token)

    input_path = Path(input_file)
    output_file = os.path.join(output_dir, f"{input_path.stem}.json")
    with open(output_file, "w") as f:
        f.write(str(json_resume.decode("utf-8")))
        f.close()

    resume_data = json.loads(json_resume)
    resume = resume_data['Value']['ResumeData']
    resume["file"] = input_file
    resumes.append(resume)

rows_list = []
for resume in resumes:
    contacts = resume.get("ContactInformation", {})

    name = contacts.get("CandidateName", {}).get("FormattedName", "No name")
    location = str( contacts.get("Location", "No location") )

    date_of_birth = resume.get("PersonalAttributes", {}).get("DateOfBirth", {}).get("Date", "")

    phones = "; ".join( map( lambda c: c.get("Raw", ""), contacts.get("Telephones", {}) ) )
    emails = "; ".join( contacts.get("EmailAddresses", []) )
    websites = "; ".join( map( lambda c: c.get("Address", ""), contacts.get("WebAddresses", {}) ) )

    summary = resume.get("ProfessionalSummary", "No summary")

    languages = "; ".join( map( lambda lc: lc.get("Language", ""), resume.get("LanguageCompetencies", {})) )

    education = "; ".join( map( lambda e: e.get("Text", ""), resume.get("EducationDetails", {})) )

    employment_history = resume.get("EmploymentHistory", {})
    experience_summary = employment_history.get("ExperienceSummary", {}).get("Description", "No experience summary")

    def create_work_experience(we):
        start_date = we.get("StartDate", {}).get("Date", "No start date")
        end_date = we.get("EndDate", {}).get("Date", "No end date")

        organization = we.get("Employer", {}).get("Name", {}).get("Raw", "No organization")
        job_title = we.get("JobTitle", {}).get("Raw", "No job title")
        job_description = we.get("Description", "No job description")

        return ", ".join([
            f"dates: {start_date}/{end_date}",
            f"organization: {organization}",
            f"job title: {job_title}",
            f"job description: {job_description}"
        ])
    work_experience = "; ".join( map(create_work_experience, employment_history.get("Positions", [])) )

    skills = "; ".join( map(lambda s: s.get("Name"), resume.get("skills", {}).get("Raw", [])) )
    certifications = "; ".join( map(lambda s: s.get("Name"), resume.get("Certifications", [])) )

    rows_list.append({
        "name": name, "date_of_birth": date_of_birth, "location": location, "phones": phones,
        "emails": emails, "websites": websites, "summary": summary, "languages": languages,
        "education": education, "profession": experience_summary, "work_experience": work_experience, "skills": skills,
        "certifications": certifications, "file": resume.get("file", "")
    })

df = pd.DataFrame(rows_list)
df.to_excel(output_dir + "/resumes.xlsx")