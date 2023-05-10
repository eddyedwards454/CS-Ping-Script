#NOTE - To be used with APIC_login3.py
from APIC_login3 import get_token
import os
import requests
import urllib3
import xlsxwriter
from csv import writer
from csv import reader
import csv

urllib3.disable_warnings()


def main():
    if os.path.exists('C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output3.csv'):
        os.remove('C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output3.csv')

    w = open('C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output3.csv', 'w')
    w.writelines('Port,Swith State,Admin State,Access VLAN,Internal VLAN ' + '\n')
    w.close()
    # aci = input("Enter APIC IP/hostname: ")
    aci = "192.168.100.10"
    token = get_token(aci)
    print("The APIC token is: " + token)
    # test = get_fabric_id(aci)
    # print(test)



def get_fabric_id(aci):
    APIC_FQDN = '192.168.100.10'
    ACI_pod = 'pod-1'
    ACI_node = 'node-111'
    aci_token = get_token(aci)
    aci_cookie = {'APIC-cookie': aci_token}
    url1 = f'https://{APIC_FQDN}/api/node/class/topology/{ACI_pod}/{ACI_node}/l1PhysIf.json'
    url2 = f'https://{APIC_FQDN}/api/node/class/topology/{ACI_pod}/{ACI_node}/ethpmPhysIf.json'
    # url3 = f'https://{APIC_FQDN}/api/node/class/fabricNode.json?'

    # print(url1)
    # print(url2)

    # aci_get = requests.get(url=url, cookies=aci_cookie, verify=False)
    aci_get = requests.get(url=url1, cookies=aci_cookie, verify=False)
    aci_get2 = requests.get(url=url2, cookies=aci_cookie, verify=False)
    # aci_get3 = requests.get(url=url3, cookies=aci_cookie, verify=False)
    fabric_id = aci_get.json()["imdata"]
    fabric_id2 = aci_get2.json()["imdata"]
    # fabric_id3 = aci_get3.json()["imdata"]
    print(fabric_id)
    print(fabric_id2)
    # print(fabric_id3)

    with open('C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output3.csv', 'wt') as csv_file:
        csv_file.writelines('Port,Swith State,Admin State,Access VLAN,Internal VLAN, Node ' + '\n')
        for item1, item2 in zip(fabric_id, fabric_id2):
            initial_data1 = item1["l1PhysIf"]["attributes"]["dn"] + ',' + item1["l1PhysIf"]["attributes"][
                "switchingSt"] + ',' + item1["l1PhysIf"]["attributes"]["adminSt"]
            initial_data2 = item2["ethpmPhysIf"]["attributes"]["accessVlan"] +'\n'

            # initial_data3 = item3["fabricNode"]["attributes"]["dn"] + '\n'
            csv_line = initial_data1 + ',' + initial_data2

            csv_file.writelines(csv_line)


if __name__ == "__main__":
    main()












