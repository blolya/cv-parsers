from pathlib import Path
from affinda import AffindaAPI, TokenCredential
import os

token = os.environ['AFFINDA_TOKEN']
credential = TokenCredential(token=token)
client = AffindaAPI(credential=credential)

file_pth = Path("/home/blolya/Documents/cv6.pdf")

with open(file_pth, "rb") as f:
    resume = client.create_resume(file=f)

print(resume.as_dict())
