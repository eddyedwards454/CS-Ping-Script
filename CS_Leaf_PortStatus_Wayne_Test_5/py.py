# from APIC_login3 import get_token
import requests
import urllib3
import os
import xlsxwriter
urllib3.disable_warnings()


def main():
    if os.path.exists('C://SCRIPTS//Learning Home Work//ACI Inventory//ACI_Node_Output1.csv'):
        os.remove('C://SCRIPTS//Learning Home Work//ACI Inventory//ACI_Node_Output1.csv')

    w = open('C://SCRIPTS//Learning Home Work//ACI Inventory//ACI_Node_Output1.csv', 'w')
    w.writelines('Port,Swith State,Admin State,Access VLAN,Internal VLAN ' + '\n')
    w.close()

    # aci = input("Enter APIC IP/hostname: ")
    aci = "192.168.100.10"
    token = get_token(aci)
    print("The APIC token is: " + token)
    test = get_fabric_id(aci)
    # print(test)

def get_token(aci):

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




def get_fabric_id(aci):
    APIC_FQDN = '192.168.100.10'
    ACI_pod = 'pod-1'
    ACI_node = 'node-111'
    aci_token = get_token(aci)
    aci_cookie = {'APIC-cookie': aci_token}
    url1 = f'https://{APIC_FQDN}/api/node/class/topology/{ACI_pod}/{ACI_node}/l1PhysIf.json'
    url2 = f'https://{APIC_FQDN}/api/node/class/topology/{ACI_pod}/{ACI_node}/ethpmPhysIf.json'
    # print(url1)
    # print(url2)

    # aci_get = requests.get(url=url, cookies=aci_cookie, verify=False)
    aci_get = requests.get(url=url1, cookies=aci_cookie, verify=False)
    aci_get2 = requests.get(url=url2, cookies=aci_cookie, verify=False)
    fabric_id = aci_get.json()["imdata"]
    fabric_id2 = aci_get2.json()["imdata"]
    print(fabric_id)
    print(fabric_id2)
    path2 = 'C:\SCRIPTS\Learning Home Work\ACI Inventory\ACI_Node_Output1.csv'

    for test in fabric_id:
        initial_data2 = test["l1PhysIf"]["attributes"]["dn"] + ',' + test["l1PhysIf"]["attributes"]["switchingSt"] + ',' + test["l1PhysIf"]["attributes"]["adminSt"]+'\n'
        print(initial_data2)
        for line in initial_data2:
            w = open(path2, 'a')
            w.writelines(line)
            w.close()

    for test in fabric_id2:
        initial_data1 = test["ethpmPhysIf"]["attributes"]["accessVlan"]+'\n'
        print(initial_data1)
        for line1 in initial_data1:
            w = open(path2, 'a')
            w.writelines(line1)
            w.close()

        # print(initial_data1)
        # filtered_data1 = list(map(get_intf_attributes1, initial_data1))
        # print(filtered_data1)

        # print(test)


    # for test1 in fabric_id:
    #     initial_data2 = test1["l1PhysIf"]["attributes"]["dn"] + " " + test1["l1PhysIf"]["attributes"]["switchingSt"] + " " + test1["l1PhysIf"]["attributes"]["adminSt"]
    #     print(initial_data2)







if __name__ == "__main__":
    main()