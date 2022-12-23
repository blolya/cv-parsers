import base64
import requests #this module will need to be installed
import json
import os.path
import datetime
 
base64str = ''
file_path = '/home/blolya/Documents/cv6.pdf'
 
with open(file_path, 'rb') as f:
    base64str = base64.b64encode(f.read()).decode('UTF-8')
 
epoch_seconds = os.path.getmtime(file_path)
last_modified_date = datetime.datetime.fromtimestamp(epoch_seconds).strftime("%Y-%m-%d") 
 
url = "https://eu-rest.resumeparsing.com/v10/parser/resume"
payload = {
  'DocumentAsBase64String': base64str,
  'DocumentLastModified': last_modified_date
}

account_id = os.environ['SOVREN_ACCOUNT_ID']
token = os.environ['SOVREN_TOKEN']
 
headers = {
  'accept': "application/json",
  'content-type': "application/json",
  'sovren-accountid': account_id,
  'sovren-servicekey': token,
}
 
response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
response_json = json.loads(response.content)
 
resume_data = response_json['Value']['ResumeData']
 
print(resume_data)
