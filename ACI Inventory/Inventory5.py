from APIC_login3 import get_token
import requests
import urllib3
import os
urllib3.disable_warnings()

def main():

   if os.path.exists('node.csv'):
        os.remove('node.csv')
    # else:
    w = open('node.csv', 'w')
    w.writelines('NodeId,Serial No, State' + '\n')
    w.close()




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
    fabric_id = aci_get.json()["imdata"]




    for test in fabric_id:
        x = (test['fabricNode']['attributes']['name']) + ',' + (test['fabricNode']['attributes']['serial']) + ',' + (test['fabricNode']['attributes']['fabricSt'] + '\n')
        print(x)
        for line in x:
            w = open('node.csv', 'a')
            w.writelines(line)



if __name__ == "__main__":
    main()