import os
import argparse
import glob
import json
from pathlib import Path
from datetime import datetime
from resume_parser import resumeparse
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
start_time = datetime.now()
for input_file in input_files:
    resume = resumeparse.read_file(input_file)

    input_path = Path(input_file)
    output_file = os.path.join(output_dir, f"{input_path.stem}.json")
    with open(output_file, "w") as f:
        f.write(json.dumps(resume))
        f.close()

    resumes.append(resume)
print(f"Parsed {len(input_files)} files in {datetime.now() - start_time}")

rows_list = []
for resume in resumes:
    name = resume.get("name", "No name")
    email = resume.get("email", "No email")
    phone = resume.get("phone", "No phone")
    skills = "; ".join( resume.get("skills", []) )

    college_name = "; ".join( resume.get("university", []) )
    degree = "; ".join( resume.get("degree", {}) )

    designation = "; ".join( resume.get("designition", []) )

    companies = "; ".join(resume.get("Companies worked at", []))

    rows_list.append({
        "name": name, "phone": phone, "email": email, "skills": skills,
        "college_name": college_name, "degree": degree, "companies": companies,
        "designation": designation
    })

df = pd.DataFrame(rows_list)
df.to_excel(output_dir + "/resumes.xlsx")
