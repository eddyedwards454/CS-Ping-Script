#NOTE to be used with APIC_login4.py Only
from APIC_login4 import get_token
import os
import requests
import urllib3
import xlsxwriter
from csv import writer
from csv import reader
import csv
urllib3.disable_warnings()


def main():
    if os.path.exists('C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output14.csv'):
        os.remove('C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output14.csv')

    # w = open('C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output9.csv', 'w')
    # w.writelines('Port,Swith State,Admin State,Access VLAN,Internal VLAN ' + '\n')
    # w.close()
    aci_devices = ["192.168.100.10"]
    for aci in aci_devices:
        print("\nAPIC: " + aci)
        # Login to APIC & get Token
        token = get_token(aci)
        print("The APIC token is: " + token + "\n")
        # Loop through Pods 1-3
        for Pod in range(1, 3):
        # for Pod in (1):

            # Loop through Nodes 1-15 (Really <Pod>01 - <Pod>15
            for NodeNum in range(11, 13):
                # Create Real ACI Node Number from Pod and NodeNum (Pad to 2 chars)
                ACI_node = f'{Pod}{NodeNum:02}'
                print("APIC: " + aci + " - Pod: " + str(Pod) + " - Node: " + str(ACI_node))

                ############################################################################
                # Call your Required Routines here, example usage within routines as follows
                ############################################################################

                # Set URL's using aci, Pod & ACI_Node vars
                aci_cookie = {'APIC-cookie': token}
                # url1 = f'https://{APIC_FQDN}/api/node/class/topology/{ACI_pod}/{ACI_node}/l1PhysIf.json'
                url1 = f'https://{aci}/api/node/class/topology/pod-{Pod}/node-{ACI_node}/l1PhysIf.json'
                url2 = f'https://{aci}/api/node/class/topology/pod-{Pod}/node-{ACI_node}/ethpmPhysIf.json'
                url3 = f'https://{aci}/api/node/class/topology/pod-{Pod}/node-{ACI_node}/vlanCktEp.json'
                # try:
                aci_get = requests.get(url=url1, cookies=aci_cookie, verify=False)
                aci_get2 = requests.get(url=url2, cookies=aci_cookie, verify=False)
                aci_get3 = requests.get(url=url2, cookies=aci_cookie, verify=False)
                fabric_id = aci_get.json()["imdata"]
                fabric_id2 = aci_get2.json()["imdata"]
                fabric_id3 = aci_get3.json()["imdata"]
                print(fabric_id3)
                ########################################################################################
                # Used to capture Errors when node or API call does not return what we are looking for #
                ########################################################################################
                if "error" in (fabric_id[0]):
                    print('Node does not exist - Continuing')
                    print(fabric_id[0])
                    # continue
                    ### WORK ON THIS BIT#####
                    with open('C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output_Nodes_Missing.csv', 'a') as csv_file:
                        csv_file.writelines('APIC,Pod,ACI_Node' + '\n')

                        # y = str(fabric_id[0]) +','+ ACI_node
                        # y = str(Pod) + ',' + ACI_node + ',' + aci
                        y = aci + ',' + str(Pod) + ',' + ACI_node
                        print(y)
                        for item3 in y:
                            csv_file.write(item3)
                    continue
                # print(fabric_id)
                # print(fabric_id2)
                #
                #
                # #############################################################################
                # # Open file and write output
                # ############################################################################
                #
                with open(
                        'C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output14.csv',
                        'a') as csv_file:
                    csv_file.writelines('APIC,Port-Node,Switch State,Admin State,Access VLAN,Internal VLAN ' + '\n')
                    for item1, item2 in zip(fabric_id, fabric_id2):
                        initial_data1 = item1["l1PhysIf"]["attributes"]["dn"] + ',' + item1["l1PhysIf"]["attributes"][
                            "switchingSt"] + ',' + item1["l1PhysIf"]["attributes"]["adminSt"]
                        initial_data2 = item2["ethpmPhysIf"]["attributes"]["accessVlan"] + "," + item2["ethpmPhysIf"]["attributes"]["allowedVlans"] +'\n'
                        # initial_data2 = item2["ethpmPhysIf"]["attributes"]["allowedVlans"] + '\n'
                        csv_line = aci + ', ' + initial_data1 + ',' + initial_data2
                        # print(csv_line)
                        csv_file.writelines(csv_line)






if __name__ == "__main__":
    main()

########## Required if you want to log the user of the script #################################
# if __name__ == "__main__":
#     text = input('Do you want to run this script  ')
#     username = input('Please enter your username please ?  ')
#     if text == 'yes' and username != '':
#         print('You have said  ' + text + '  and your username is ' + username + ' name will be logged !')
#         with open(
#
#                 'C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Username15.csv',
#                 'w') as csv_file:
#             csv_file.writelines('Answer,Username,' + '\n')
#             f = text + ',' + username
#             csv_file.writelines(f)
#         main()
#
#     else:
#         print('You have not said Yes to run the script - Script will not run needs to be ''yes'' ')