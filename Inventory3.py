from APIC_login3 import get_token
import requests
import urllib3
import os
urllib3.disable_warnings()

def main():
    # aci = input("Enter APIC IP/hostname: ")
    path = 'C://SCRIPTS//Learning Home Work//ACI_IP.txt'
    # with open("ACI_IP.txt") as file:
    with open(path, 'r') as file:
        my_devices = file.readlines()
        for line in my_devices:
            aci = line.rstrip()
            print("You are logging in to : "  + aci)
            token = get_token(aci)
            print("The APIC token is: " + token)
            test = get_fabric_id(aci)
            print(test)


def get_fabric_id(aci): # Get Fabric Nodes
    aci_token = get_token(aci)
    aci_cookie = {'APIC-cookie': aci_token}
    url = ('https://' + aci + '/api/node/class/fabricNode.json?')

    # url = ('https://' + aci + '/api/node/mo/uni/tn-Wayne_Edwards_Tenant.json?query-target=children&target-subtree-class=fvBD')
    aci_get = requests.get(url=url, cookies=aci_cookie, verify=False)
    # fabric_id = aci_get.json()["imdata"][0]["topSystem"]["attributes"]["fabricId"]
    # fabric_id = aci_get.json()["imdata"][0]["topSystem"]["attributes"]
    # fabric_id = aci_get.json()["imdata"][0]["topSystem"]
    # fabric_id = aci_get.json()["imdata"][0]["topSystem"]["children"][0]["healthInst"]["attributes"]["twScore"]
    # for k,v in
    fabric_id = aci_get.json()["imdata"]
    # print(len(aci_get.json()))
    # print(fabric_id)
    # answer2 = input("Do you want to backup the device now  ? (yes or no)\n\n\n ")
    # if os.path.exists('BD.txt.txt'):
    #     os.remove('BD.txt.txt')
    # else:
    #     w = open('BD.txt', 'w')
    # if not any(answer2.lower() == f for f in ["1", 'No', 'no', 'n']):
    #     pass
    # else:



    for test in fabric_id:
    #      # print(test)
    #      # print(test['fvBD']['attributes']['name'])
    #      # print("Bridge Domains : "  + test['fvBD']['attributes']['name'] +'\n')
    #      # x = ("Bridge Domains : " + test['dhcpClient']['attributes'] + '\n')
         x = ' Node is : ' + '  ' + (test['fabricNode']['attributes']['name']) + '  ' + 'The serial number is :   ' + (test['fabricNode']['attributes']['serial']) + ' The state is :  ' +  (test['fabricNode']['attributes']['fabricSt'])
         print(x)

         # for line in x:
         #     w = open('BD.txt','a')
         #     w.write(line)

if __name__ == "__main__":
    main()