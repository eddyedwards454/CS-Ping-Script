import requests
import sys
import urllib3
urllib3.disable_warnings()


# Get APIC token
def get_token(aci):
    aci = input("Enter APIC IP/hostname: ")
    # aci = '192.168.100.10'
    login_url = ('https://' + aci + '/api/aaaLogin.json')
    login_username = "admin"
    login_password = "Jennygbmwx5!"
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


def main():
    aci = input("Enter APIC IP/hostname: ")

    token = get_token(aci)
    print("The APIC token is: " + token)


if __name__ == "__main__":
    main()