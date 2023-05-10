import requests
import json

# url = "https://192.168.100.10/api/aaaLogin.json"
# payload = {
#    "aaaUser": {
#       "attributes": {
#          "name": "admin",
#          "pwd": "Jennygbmwx5!"
#       }
#    }
#
#
# headers = {
#    "Content-Type" : "application/json"
# }
# requests.packages.urllib3.disable_warnings()
# response = requests.post(url,data=json.dumps(payload), headers=headers, verify=False).json()
# token = response['imdata'][0]['aaaLogin']['attributes']['token']
# return token
# token1 = get_token(token)
# print(token1)


   # url = "https://192.168.100.15/api/aaaLogin.json"
#
#    payload = {
#       "aaaUser": {
#          "attributes": {
#             "name":"admin",
#             "pwd":"Jennygbmwx5!"
#          }
#       }
#    }
#
#    headers = {
#       "Content-Type" : "application/json"
#    }
#
#    requests.packages.urllib3.disable_warnings()
#    response = requests.post(url,data=json.dumps(payload), headers=headers, verify=False).json()
#
#    token = response['imdata'][0]['aaaLogin']['attributes']['token']
#    return token
#
# def main():
#    token = get_token()
#    print("The token is: " + token)
#
# # if __name__ == "__main__":
# #    main()


def get_token():
   url = "https://192.168.100.10/api/aaaLogin.json"

   payload = {
      "aaaUser": {
         "attributes": {
            "name":"admin",
            "pwd":"Jennygbmwx5!"
         }
      }
   }

   headers = {
      "Content-Type" : "application/json"
   }

   requests.packages.urllib3.disable_warnings()
   response = requests.post(url,data=json.dumps(payload), headers=headers, verify=False).json()

   token = response['imdata'][0]['aaaLogin']['attributes']['token']
   return token

def main():
   token = get_token()
   print("The token is: " + token)




if __name__ == "__main__":
   main()
