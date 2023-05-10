from APIC_login import get_token
import requests
import urllib3
urllib3.disable_warnings()


# Get APIC token
def get_token(aci):
    login_url = ('https://' + aci + '/api/aaaLogin.json')
    login_username = input("Enter APIC username: ")
    login_password = input("Enter APIC password: ")
    login_payload = {"aaaUser": {"attributes": {"name": login_username, "pwd": login_password}}}
    aci_login = requests.post(url=login_url, json=login_payload, verify=False)

    if aci_login.status_code == 200:
        print("\nLogin Successful!\n")
        aci_token = aci_login.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]
        return aci_token
    else:
        print("\nError below:")
        print(aci_login.json())
        sys.exit()


# Get Fabric ID
def get_fabric_id(aci, aci_cookie):
    url = ('https://' + aci + '/api/node/mo/topology/pod-1/node-1/sys.json?rsp-subtree-include=health,fault-count')
    aci_get = requests.get(url=url, cookies=aci_cookie, verify=False)
    fabric_id = aci_get.json()["imdata"][0]["topSystem"]["attributes"]["fabricId"]
    return fabric_id


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


if __name__ == "__main__":
   # backup()
   get_fabric_id()