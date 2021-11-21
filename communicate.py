import requests
import json
payload={}
headers = {}

response = requests.request("GET", 'http://192.168.0.6:5000/chain', headers=headers, data=payload)
print(response.text)

response = requests.request("GET", 'http://192.168.0.6:5000/mine', headers=headers, data=payload)
print(response.text)

response = requests.request("GET", 'http://192.168.0.6:5000/chain', headers=headers, data=payload)
print(response.text)

url = "http://192.168.0.6:5001/nodes/register"

payload = json.dumps({
  "nodes": [
    "http://192.168.0.6:5000"
  ]
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
response = requests.request("GET", 'http://192.168.0.6:5001/nodes/resolve')
print(response.text)
input()