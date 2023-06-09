from APIC_login3 import get_token
import requests
import urllib3
import os
urllib3.disable_warnings()


def main():
    # aci = input("Enter APIC IP/hostname: ")

    if os.path.exists('C://SCRIPTS//Learning Home Work//ACI Inventory//ACI_Node_Output.csv'):
        os.remove('C://SCRIPTS//Learning Home Work//ACI Inventory//ACI_Node_Output.csv')

    w = open('C://SCRIPTS//Learning Home Work//ACI Inventory//ACI_Node_Output.csv', 'w')
    w.writelines('Serial,Mgt Address,Model,Role,DN,Version  ' + '\n')
    w.close()
    path = 'C://SCRIPTS//Learning Home Work//ACI Inventory//ACI_IP.txt'
    # with open("ACI_IP.txt") as file:
    with open(path, 'r') as file:

        my_devices = file.readlines()
# the for loop reads the ACI_IP.text file and inputs varibale 'aci'
        for line in my_devices:
            aci = line.rstrip()
            print("You are logging in to : " + "\n" + aci)
            # print("The APIC token is: " + token)
            #The below command calls the get_fabric_fucntion below
            get_fabric_id(aci)
            # print(test)


def get_fabric_id(aci):  # Get Fabric Nodes
    aci_token = get_token(aci)
    aci_cookie = {'APIC-cookie': aci_token}
    url = ('https://' + aci + '/api/node/class/fabricNode.json?')
    aci_get = requests.get(url=url, cookies=aci_cookie, verify=False)
    fabric_id = aci_get.json()["imdata"]
    print(fabric_id)
    for test in fabric_id:

        # x = (test['fabricNode']['attributes']['name']) + ',' + (test['fabricNode']['attributes']['serial']) + ',' + (
        #             test['fabricNode']['attributes']['fabricSt'] + ',' + (test['fabricNode']['attributes']['address']) + ','
        #             + (test['fabricNode']['attributes']['model'])+ ',' + (test['fabricNode']['attributes']['role']) +
        #             ',' + (test['fabricNode']['attributes']['version'])+ ',' + (test['fabricNode']['attributes']['dn']) +'\n')

        x = (test['fabricNode']['attributes']['serial']) + ',' + (test['fabricNode']['attributes']['address']) + ',' + (
                    test['fabricNode']['attributes']['model'] + ',' + (test['fabricNode']['attributes']['role']) + ','
                    + (test['fabricNode']['attributes']['dn'])+ ',' + (test['fabricNode']['attributes']['version'])  +'\n')

        print(x)



        path2 = 'C:\SCRIPTS\Learning Home Work\ACI Inventory\ACI_Node_Output.csv'

        for line in x:
            w = open(path2, 'a')

            w.writelines(line)


if __name__ == "__main__":
    main()