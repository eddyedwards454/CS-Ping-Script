from APIC_login3 import get_token
import requests
import urllib3
import os

urllib3.disable_warnings()


def main():
    aci = input("Enter APIC IP/hostname: ")
    token = get_token(aci)
    print("The APIC token is: " + token)
    test = get_fabric_id(aci)
    # test2 = get_fabric_id2(aci)
    print(test)
    # print(test2)

def get_fabric_id(aci):  # Get Fabric Nodes
    aci_token = get_token(aci)
    aci_cookie = {'APIC-cookie': aci_token}
    url = ('https://' + aci + '/api/node/mo/topology/pod-1/node-101/sys/phys-[eth1/5].json')
    aci_get = requests.get(url=url, cookies=aci_cookie, verify=False)
    fabric_id = aci_get.json()["imdata"]
    # print(len(aci_get.json()))
    print(fabric_id)
    for test in fabric_id:
        x = (test['l1PhysIf']['attributes']['adminSt'] + '\n')
        print(x)
#     #     for line in x:
    #         w = open('node.csv', 'a')
    #         w.writelines(line)


#
# def get_fabric_id(aci):  # Get Fabric Nodes
#     aci_token = get_token(aci)
#     aci_cookie = {'APIC-cookie': aci_token}
#     url = ('https://' + aci + '/api/node/class/fabricNode.json?')
#     aci_get = requests.get(url=url, cookies=aci_cookie, verify=False)
#     fabric_id = aci_get.json()["imdata"]
#     # print(len(aci_get.json()))
#     # print(fabric_id)
#     for test in fabric_id:
#         x = (test['fabricNode']['attributes']['id'] + '\n')
#         print(x)
# #     #     for line in x:
#     #         w = open('node.csv', 'a')
#     #         w.writelines(line)

# def get_fabric_id2(aci):
#     aci_token = get_token(aci)
#     aci_cookie = {'APIC-cookie': aci_token}
#     # url = ('https://' + aci + '/api/node/class/fabricNode.json?')
#     url = ('https://' + aci + 'api/node/mo/topology/pod-1/node-101/sys.json')
#     aci_get = requests.get(url=url, cookies=aci_cookie, verify=False)
#     fabric_id2 = aci_get.json()["imdata"]
#     # print(len(aci_get.json()))
#     print(fabric_id2)
#     # for test2 in fabric_id2:
#     #     x = (test2['l1PhysIf']['attributes']['adminSt'] + '\n')
#     #     print(x)


if __name__ == "__main__":
    main()
