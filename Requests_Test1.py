import requests
import urllib3
from APIC_login2 import get_token
urllib3.disable_warnings()
aci = "192.168.100.10"
aci_token = get_token(aci)


url = "https://192.168.100.10/api/node/mo/uni/tn-Python.json"

payload = "{\n    \"fvTenant\": {\n        \"attributes\": {\n            \"dn\": \"uni/tn-Python\",\n            \"status\": \"deleted\"\n        },\n        \"children\": []\n    }\n}"
headers = {
  'Content-Type': 'application/json',
  'User-Agent': 'PostmanRuntime/7.22.0',
  'Accept': '*/*',
  'Cache-Control': 'no-cache',
  'Postman-Token': 'bad7185d-1817-4e09-8dc3-bec4b82e24bc',
  'Host': '192.168.100.10',
  'Accept-Encoding': 'gzip, deflate, br',
  'Content-Length': '159',
  'Connection': 'keep-alive'
}

response = requests.request("POST", url, headers=headers, data = payload, cookies= aci_token, verify=False)

print(response.text.encode('utf8'))

# payload = "{\n    \"fvTenant\": {\n        \"attributes\": {\n            \"dn\": \"uni/tn-Python\",\n            \"status\": \"created\"\n        },\n        \"children\": []\n    }\n}"
# headers = {
#   'Content-Type': 'application/json',
#   'User-Agent': 'PostmanRuntime/7.22.0',
#   'Accept': '*/*',
#   'Cache-Control': 'no-cache',
#   'Postman-Token': 'bad7185d-1817-4e09-8dc3-bec4b82e24bc',
#   'Host': '192.168.100.10',
#   'Accept-Encoding': 'gzip, deflate, br',
#   'Content-Length': '159',
#   'Cookie': 'APIC-cookie=eyJhbGciOiJSUzI1NiIsImtpZCI6ImJ4b2dnYTV2ODJvc3hmY2FjYWhweW55cjZ2MjA3aHluIiwidHlwIjoiand0In0.eyJyYmFjIjpbeyJkb21haW4iOiJhbGwiLCJyb2xlc1IiOjAsInJvbGVzVyI6MX1dLCJpc3MiOiJBQ0kgQVBJQyIsInVzZXJuYW1lIjoiYWRtaW4iLCJ1c2VyaWQiOjE1Mzc0LCJ1c2VyZmxhZ3MiOjAsImlhdCI6MTY2ODA3NDk4NywiZXhwIjoxNjY4MDc1NTg3LCJzZXNzaW9uaWQiOiJBMWMyUEc2blQ1T3U2dDJYV0NoK05BPT0ifQ.fCUd5buNaI3A9E_7kiUgmiW_KUW1CIwhg6Zjw7JrK1yRfDCGdEk66GZIF4TTwbUWTYkugTav4xLTcdatpE3SwpGQR1WeGunqO06LBf1lFDONg0DN0boXBpKBWdoE87ICC8WBUE7WWyud5IUAo6xeDJzt1GHYw3arNE9Q9tvqUDbY045e0eXpaPLQSS9D8KVyxFGQkUSO9wC_FDC96daZ7_0mAo9w-wkZWz-oxo1nnXEvsXInDGUrWGJEQ4LTan1LyXzxRv1aeWJbx9MBahrWSrv9V0YjsqvP0f0MerntC53LGW49u4AKIzJI9wzIXF07gCtV1zAvrW0klTq0YLnLvg',
#   'Connection': 'keep-alive'
# }
#
# response = requests.request("POST", url, headers=headers, data = payload, verify=False)
#
# print(response.text.encode('utf8'))

