from APIC_login import get_token
import requests
import urllib3
urllib3.disable_warnings()


def backup():
    aci = input("Enter APIC IP/hostname: ")
    aci_token = get_token(aci)
    aci_cookie = {'APIC-cookie': aci_token}
    url = ('https://' + aci + '/api/node/mo/uni.json')
    filename = input("Enter your backup filename: ")
    payload = {
        "configExportP": {
            "attributes": {
                "dn": "uni/fabric/configexp-defaultOneTime",
                "name": "defaultOneTime",
                "snapshot": "true",
                "targetDn": "",
                "adminSt": "triggered",
                "rn": "configexp-defaultOneTime",
                "descr": filename
            }
        }
    }
    aci_post = requests.post(url=url, json=payload, cookies=aci_cookie, verify=False)
    if aci_post.json()["totalCount"] == '0':
        print("\nBackup created successfully !")
    else:
        print("\nResponse below:")
        print(aci_post.json())

print(aci_token)
if __name__ == "__main__":
    backup()
