from APIC_login4 import get_token
import os
import requests
import urllib3
import xlsxwriter
from csv import writer
from csv import reader
import csv
urllib3.disable_warnings()

def get_intf_attributes1(initial_intf_data):
    return initial_intf_data['l1PhysIf']['attributes']

def get_intf_attributes2(initial_intf_data):
    return initial_intf_data['ethpmPhysIf']['attributes']

def get_real_vlans(initial_vlan_data):
    # Takes a list of dicts, returns a dict where
    # keys are internal VLAN numbers, values are real VLAN numbers.
    mapped_vlans = {}
    for vlan_data in initial_vlan_data:
        mapped_vlans[vlan_data['vlanCktEp']['attributes']['id']] = vlan_data['vlanCktEp']['attributes']['encap'].lstrip(
            'vlan-')
        # mapped_vlans[vlan_data['vlanCktEp']['attributes']['id']] = vlan_data['vlanCktEp']['attributes']['encap']
        # # print(vlan_data)
    return mapped_vlans
##### Below - Combines to lists into one ################
def combine_intf_attributes(data1, data2):
    combined_intf_data = []
    for d1, d2 in zip(data1, data2):
        inner_dict = {}
        inner_dict['id'] = d1['id']
        inner_dict['descr'] = d1['descr']
        inner_dict['adminSt'] = d1['adminSt']
        inner_dict['operSt'] = d2['operSt']
        inner_dict['operStQual'] = d2['operStQual']
        inner_dict['layer'] = d1['layer']
        inner_dict['mode'] = d1['mode']
        inner_dict['operSpeed'] = d2['operSpeed']
        inner_dict['operDuplex'] = d2['operDuplex']
        inner_dict['mtu'] = d1['mtu']
        inner_dict['operVlans'] = d2['operVlans']
        inner_dict['nativeVlan'] = d2['nativeVlan']
        inner_dict['autoNeg'] = d1['autoNeg']
        inner_dict['spanMode'] = d1['spanMode']
        combined_intf_data.append(inner_dict)
    return combined_intf_data

def expand_vlans(vlans_list):
    # Takes input like '10,11-13' and returns ['10', '11', '12', '13']
    final_vlans_list = []
    vlans_list = vlans_list.split(',')
    for item in vlans_list:
        if '-' in item:
            range_start, _, range_end = item.strip().partition('-')
            for num in range(int(range_start), int(range_end) + 1):
                final_vlans_list.append(str(num))
        else:
            final_vlans_list.append(item.strip())
    return final_vlans_list
def main():
    if os.path.exists('C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output23.csv'):
        os.remove('C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output23.csv')
    w = open('C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output23.csv', 'w')
    w.writelines('APIC,Pod,Node,Port,Description,Adminstate,Native_vlan,Layer,Operate_Speed,MTU,SFP,Encap-VLAN,Encap-VLAN1,Encap-VLAN2,Encap-VLAN3,Encap-VLAN4,Encap-VLAN5,Encap-VLAN6,Encap-VLAN7,Encap-VLAN8,Encap-VLAN9,Encap-VLAN10,Encap-VLAN11,Encap-VLAN12,Encap-VLAN13,Encap-VLAN14,Encap-VLAN15,Encap-VLAN16,Encap-VLAN17,Encap-VLAN17,Encap-VLAN19,Encap-VLAN20,Encap-VLAN21,Encap-VLAN22,Encap-VLAN23,Encap-VLAN24,Encap-VLAN25,Encap-VLAN26,Encap-VLAN27,Encap-VLAN28,Encap-VLAN29,Encap-VLAN30,Encap-VLAN31,Encap-VLAN32,Encap-VLAN33,Encap-VLAN34'  + '\n')
    # z = (aci + ',' + ACI_node + ',' + pods + ',' + port + ','+ desc + ',' + adminstate + ',' + native_vlan + ',' + layer + ',' + operate_speed + ',' + mtu + ',' + sfp + ',' + encap_vlan + '\n')
    w.close()
    if os.path.exists(
            'C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output_Nodes_Missing23.csv'):
        os.remove(
            'C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output_Nodes_Missing23.csv')
    w = open(
        'C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output_Nodes_Missing23.csv','w')
    w.writelines('APIC,Pod,ACI_Node_Not_Available' + '\n')
    w.close()
    # aci_devices = ["sloas0101.link.hedani.net","gshas0101.link.hedani.net","prias0101.link.hedani.net","cdcas0101.link.hedani.net","sipas0101.link.hedani.net","juras0101.link.hedani.net"]
    # aci_devices = ["sipas0101.link.hedani.net","juras0101.link.hedani.net"]
    aci_devices = ["heqas0101.link.hedani.net","hk1as0101.link.hedani.net"]
    aci_devices = ["192.168.100.10"]
    for aci in aci_devices:
        print("\nAPIC: " + aci)
        # Login to APIC & get Token
        token = get_token(aci)
        print("The APIC token is: " + token + "\n")
        # Loop through Pods 1-3
        for Pod in range(1, 2):
            # for Pod in (1):
            # Loop through Nodes 1-15 (Really <Pod>01 - <Pod>15
            for NodeNum in range(11, 13 ):
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
                aci_get = requests.get(url=url1, cookies=aci_cookie, verify=False)
                aci_get2 = requests.get(url=url2, cookies=aci_cookie, verify=False)
                aci_get3 = requests.get(url=url3, cookies=aci_cookie, verify=False)
                initial_intf_data1 = aci_get.json()["imdata"]
                initial_intf_data2 = aci_get2.json()["imdata"]
                initial_vlan_data = aci_get3.json()["imdata"]
                ################Catches Errors if Node does not exist  ########################
                if "error" in (initial_intf_data1[0]):
                    print('Node does not exist - Continuing')
                    # print(initial_vlan_data[0])
                    ### WORK ON THIS BIT#####
                    with open(
                            'C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output_Nodes_Missing23.csv','a') as csv_file:
                        y = aci + ',' + str(Pod) + ',' + ACI_node + '\n'
                        # print(y)
                        csv_file.write(y)
                    continue
                #########Calls Function Get_intf_attributes get attribtues for l1PhysIf (Port Status Up/Down ect  and ethpmPhysIf(operational-vlans = Internal Vlans)  ######
                filtered_intf_data1 = list(map(get_intf_attributes1, initial_intf_data1))
                filtered_intf_data2 = list(map(get_intf_attributes2, initial_intf_data2))
                # print(filtered_intf_data1)
                # print(filtered_intf_data2)
                ##############Mapped_Vlans ID and ENCAP together into a DICT- See Function get_real_vlans above ##############
                # print(initial_vlan_data)
                mapped_vlans = get_real_vlans(initial_vlan_data)
                # print(mapped_vlans)

                ####################Comnines data from Data1 Atrributies and Data2 Attributies in to a list - See Function "combine_intf_attributes Creates Dict look for Operational Vlan"
                initial_intf_data = combine_intf_attributes(filtered_intf_data1, filtered_intf_data2)
                # print(initial_intf_data)

                ####################Pulling the two togather- initial_initial_data now as operVlans in it ######################

                final_intf_data = []
                for intf_data in initial_intf_data:
                    ### Turn VLANs list from string like '10-11,14' into list like ['10', '11', '14'] using Function expanded_vlans above
                    expanded_vlans = expand_vlans(intf_data['operVlans'])
                    # print(expanded_vlans)
                    # #     # Search expanded_vlans in mapped_vlans to get real VLANs
                    real_vlans = []
                    for vlan in expanded_vlans:
                        if mapped_vlans.get(vlan):
                            real_vlans.append(mapped_vlans.get(vlan))
                    real_vlans.sort()
                    # print(real_vlans)
                    ##### Change real_vlans from list to string, and swap internal VLANs with it
                    real_vlans = ', '.join(real_vlans)
                    intf_data['operVlans'] = real_vlans
                    #     # Change native VLAN to real native VLAN
                    intf_data['nativeVlan'] = mapped_vlans.get(intf_data['nativeVlan'].lstrip('vlan-'))
                    final_intf_data.append(intf_data)
                    # print(final_intf_data)
                ##############Output to file############################
                for item in final_intf_data:
                    port = str(item['id'])
                    encap_vlan = str(item['operVlans'])
                    native_vlan = str(item['nativeVlan'])
                    adminstate = str(item['operSt'])
                    desc = str(item['descr'])
                    layer = str(item['layer'])
                    operate_speed= str(item['operSpeed'])
                    mtu = str(item['mtu'])
                    sfp = str(item['operStQual'])
                    pods = str(Pod)
                    # z = ('The port is ' + y + ',' + ' the vlans are  ' + ', ' + w + '\n')
                    z = (aci + ',' + ACI_node + ',' + pods + ',' + port + ','+ desc + ',' + adminstate + ',' + native_vlan + ',' + layer + ',' + operate_speed + ',' + mtu + ',' + sfp + ',' + encap_vlan + '\n')
                    with open(
                            'C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output23.csv','a') as csv_file:
                        csv_file.write(z)
if __name__ == "__main__":
    main()



######### Required if you want to log the user of the script #################################

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
#
#
#     else:
#         print('You have not said Yes to run the script - Script will not run needs to be ''yes'' ')

