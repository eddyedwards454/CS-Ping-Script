import requests
import sys
import urllib3
from getpass import getpass
urllib3.disable_warnings()
import os

# Get APIC token
def get_token(aci):
    # aci = '192.168.100.10'
    login_url = ('https://' + aci + '/api/aaaLogin.json')
    # login_username = input("Enter APIC username: ")
    # login_password = input("Enter APIC password: ")
    login_username = "admin"
    # login_password = getpass()
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

