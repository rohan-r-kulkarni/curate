import requests

session = requests.Session()
ieor = "http://www.columbia.edu/cu/bulletin/uwb/sel/DANB_Fall2018_text.html"

resp = session.get(ieor)

print(dir(resp))
print(resp.text)

#
# print(resp.content)