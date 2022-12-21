from pyresparser import ResumeParser
data = ResumeParser('/home/blolya/Documents/cv6.pdf').get_extracted_data()
print(data)
