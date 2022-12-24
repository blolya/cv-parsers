import base64
import requests
import json
import os.path
import datetime
import glob
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
 
def parse(file, account_id, token):
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
    json_resume = parse(input_file, account_id, token)

    input_path = Path(input_file)
    output_file = os.path.join(output_dir, f"{input_path.stem}.json")
    with open(output_file, "w") as f:
        f.write(str(json_resume.decode("utf-8")))
        f.close()

    resume_data = json.loads(json_resume)
    resume = resume_data['Value']['ResumeData']
    resumes.append(resume)

for resume in resumes:
    print(resume["ContactInformation"])