from APIC_login3 import get_token
import requests
import urllib3
urllib3.disable_warnings()

def main():
    # aci = input("Enter APIC IP/hostname: ")
    aci = "192.168.100.15"
    token = get_token(aci)
    print("The APIC token is: " + token)
    test = get_fabric_id(aci)
    print(test)



# def get_token(aci):
#     login_url = ('https://' + aci + '/api/aaaLogin.json')
#     login_username = input("Enter APIC username: ")
#     login_password = input("Enter APIC password: ")
#     login_payload = {"aaaUser": {"attributes": {"name": login_username, "pwd": login_password}}}
#     aci_login = requests.post(url=login_url, json=login_payload, verify=False)
#
#     if aci_login.status_code == 200:
#         print("\nLogin Successful!\n")
#         aci_token = aci_login.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]
#         return aci_token
#     else:
#         print("\nError below:")
#         print(aci_login.json())
#         sys.exit()



# def get_fabric_id(aci):
#     aci_token = get_token(aci)
#     aci_cookie = {'APIC-cookie': aci_token}
#     url = ('https://' + aci + 'api/node/mo/topology/pod-1/node-101/sys.json?rsp-subtree-include=health,fault-count')
#     aci_get = requests.get(url=url, cookies=aci_cookie, verify=False)
#     # fabric_id = aci_get.json()["imdata"][0]["topSystem"]["attributes"]["fabricId"]
#     # fabric_id = aci_get.json()["imdata"][0]["topSystem"]["attributes"]
#     # fabric_id = aci_get.json()["imdata"][0]["topSystem"]
#     # for test in aci_get.json
#     # print(aci_get.json())
#     # print(len(aci_get.json()))
#     # for i in aci_get.json:
#     #     print(i)
#     # print(aci_get.json()
#     fabric_id = aci_get.json()["imdata"][0]["topSystem"]["children"][0]["healthInst"]["attributes"]["twScore"]
#     # fabric_id = aci_get.json()["imdata"][0]["topSystem"]["children"][0]["healthInst"]["attributes"]["twScore"]
#     return fabric_id

# def get_fabric_id(aci):
#     aci_token = get_token(aci)
#     aci_cookie = {'APIC-cookie': aci_token}
#     url = ('https://' + aci + '/api/node/class/fabricNode.json')
#     aci_get = requests.get(url=url, cookies=aci_cookie, verify=False)
#     # fabric_id = aci_get.json()["imdata"][0]["topSystem"]["attributes"]["fabricId"]
#     # fabric_id = aci_get.json()["imdata"][0]["topSystem"]["attributes"]
#     # fabric_id = aci_get.json()["imdata"][0]["topSystem"]
#     # fabric_id = aci_get.json()["imdata"][0]["topSystem"]["children"][0]["healthInst"]["attributes"]["twScore"]
#     # for k,v in
#     fabric_id = aci_get.json()["imdata"]
#     # print(len(aci_get.json()))
#     for test in fabric_id:
#         # print(test)
#         # print(test['fabricNode']['attributes'])
#         print("You have the following nodes : "  + test['fabricNode']['attributes']['dn'])
#         print("The serial numbers for the above is  : " +  test['fabricNode']['attributes']['serial'])
#
#
#     return fabric_id

def get_fabric_id(aci):
    aci_token = get_token(aci)
    aci_cookie = {'APIC-cookie': aci_token}
    url = ('https://' + aci + '/api/node/class/topology/pod-1/node-111/l1PhysIf.json')
    url2 = ('https://' + aci + '/api/node/class/topology/pod-1/node-111/ethpmPhysIf.json')

    aci_get = requests.get(url=url, cookies=aci_cookie, verify=False)
    fabric_id = aci_get.json()["imdata"][0]["l1PhysIf"]["attributes"]["dn"]
    # fabric_id = aci_get.json()["imdata"][0]["topSystem"]["attributes"]
    # fabric_id = aci_get.json()["imdata"][0]["topSystem"]
    # fabric_id = aci_get.json()["imdata"][0]["topSystem"]["children"][0]["healthInst"]["attributes"]["twScore"]
    # for k,v in
    # fabric_id = aci_get.json()["imdata"]
    print(fabric_id)

    aci_get2 = requests.get(url=url2, cookies=aci_cookie, verify=False)
    fabric_id2 = aci_get2.json()["imdata"]
    print(fabric_id2)
    # print(len(aci_get.json()))
    for test in fabric_id:
        # print(test)
        # print(test['fabricNode']['attributes'])
        # print("You have the following nodes : "  + test["l1PhysIf"]['attributes']['dn'])
        print("You have the following nodes : "  + str(test["imdata"][0]["l1PhysIf"]["attributes"]["dn"])
        # print("The serial numbers for the above is  : " +  test['fabricNode']['attributes']['serial'])


    # return fabric_id
    # return fabric_id2
    # return fabric_id



if __name__ == "__main__":
    main()