import os
import argparse
import glob
import json
from pathlib import Path
from pyresparser import ResumeParser
import pandas as pd

arg_parser = argparse.ArgumentParser(prog="Pyresparser", description="Parsing resumes using pyresparser library")
arg_parser.add_argument("-id", "--input_dir", help="Input directory of resume files")
arg_parser.add_argument("-od", "--output_dir", help="Output directory of resume files")
arg_parser.add_argument("-e", "--exts", nargs='+', help="Extensions to parse. All if empty.")
args = arg_parser.parse_args()

input_dir = args.input_dir
output_dir = args.output_dir
exts = args.exts

if input_dir is None:
    arg_parser.print_help()
    raise Exception("Must specify input directory of the resumes")
if output_dir is None:
    arg_parser.print_help()
    raise Exception("Must specify output directory of the resumes")

input_files = glob.glob(input_dir + "/*")
input_files = list( filter(lambda f: Path(f).suffix in exts, input_files) ) \
    if len(exts) > 0 \
    else input_files

resumes = []
for input_file in input_files:
    resume = ResumeParser(input_file).get_extracted_data()
    
    # removing keys with None value
    # to avoid conditioning during parsing
    for k in list(resume):
        if resume[k] == None:
            del resume[k]

    input_path = Path(input_file)
    output_file = os.path.join(output_dir, f"{input_path.stem}.json")
    with open(output_file, "w") as f:
        f.write(json.dumps(resume))
        f.close()

    resumes.append(resume)

rows_list = []
for resume in resumes:
    name = resume.get("name", "No name")
    email = resume.get("email", "No email")
    phone = resume.get("mobile_number", "No phone")
    skills = "; ".join( resume.get("skills", []) )

    college_name = resume.get("college_name", "")
    degree = "; ".join( resume.get("degree", {}) )
    education = f"{college_name}: {degree}"

    designation = "; ".join(resume.get("designation", []))
    experience = "; ".join(resume.get("experience", []))

    companies = "; ".join(resume.get("company_names", []))

    rows_list.append({
        "name": name, "phone": phone, "email": email, "skills": skills,
        "education": education, "profession": designation, "work_experience": experience,
        "companies": companies
    })

df = pd.DataFrame(rows_list)
df.to_excel(output_dir + "/resumes.xlsx")
