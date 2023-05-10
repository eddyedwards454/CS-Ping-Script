import requests
import sys
import urllib3
from getpass import getpass
urllib3.disable_warnings()
import os

def main():
    #Removes existing file
    if os.path.exists('C://SCRIPTS//Learning Home Work//ACI Inventory//ACI_Node_Output3.csv'):
        os.remove('C://SCRIPTS//Learning Home Work//ACI Inventory//ACI_Node_Output3.csv')
    #Creates new File
    w = open('C://SCRIPTS//Learning Home Work//ACI Inventory//ACI_Node_Output3.csv', 'w')
    w.writelines('Port,Swith State,Admin State,Access VLAN,Internal VLAN ' + '\n')
    w.close()
    #Open and reads APIC addresses
    path = 'C://SCRIPTS//Learning Home Work//ACI Inventory//ACI_IP.txt'
    with open(path, 'r') as file:
        my_devices = file.readlines()
        # the for loop reads the ACI_IP.text file and inputs varibale 'aci'
        for line in my_devices:
            aci = line.rstrip()
            print("You are logging in to : " + "\n" + aci)
            # print("The APIC token is: " + token)
            # The below command calls the get_fabric_fucntion below
            # print(aci)
            get_token(aci)
            # get_fabric_id(aci)
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


# Get Fabric ID
if __name__ == "__main__":
    main()
