from utils.aci_api import APIC, APICError

# def get_intf_attributes1(initial_intf_data):
#     return initial_intf_data['l1PhysIf']['attributes']
#
# def get_intf_attributes2(initial_intf_data):
#     return initial_intf_data['ethpmPhysIf']['attributes']
#
# def get_real_vlans(initial_vlan_data):
#     # Takes a list of dicts, returns a dict where
#     # keys are internal VLAN numbers, values are real VLAN numbers.
#     mapped_vlans = {}
#     for vlan_data in initial_vlan_data:
#         mapped_vlans[vlan_data['vlanCktEp']['attributes']['id']] = vlan_data['vlanCktEp']['attributes']['encap'].lstrip(
#             'vlan-')
#     return mapped_vlans

# def combine_intf_attributes(data1, data2):
#     combined_intf_data = []
#     for d1, d2 in zip(data1, data2):
#         inner_dict = {}
#         inner_dict['id'] = d1['id']
#         inner_dict['descr'] = d1['descr']
#         inner_dict['adminSt'] = d1['adminSt']
#         inner_dict['operSt'] = d2['operSt']
#         inner_dict['operStQual'] = d2['operStQual']
#         inner_dict['layer'] = d1['layer']
#         inner_dict['mode'] = d1['mode']
#         inner_dict['operSpeed'] = d2['operSpeed']
#         inner_dict['operDuplex'] = d2['operDuplex']
#         inner_dict['mtu'] = d1['mtu']
#         inner_dict['operVlans'] = d2['operVlans']
#         inner_dict['nativeVlan'] = d2['nativeVlan']
#         inner_dict['autoNeg'] = d1['autoNeg']
#         inner_dict['spanMode'] = d1['spanMode']
#         combined_intf_data.append(inner_dict)
#     return combined_intf_data


# def expand_vlans(vlans_list):
#     # Takes input like '10,11-13' and returns ['10', '11', '12', '13']
#     final_vlans_list = []
#     vlans_list = vlans_list.split(',')
#     for item in vlans_list:
#         if '-' in item:
#             range_start, _, range_end = item.strip().partition('-')
#             for num in range(int(range_start), int(range_end) + 1):
#                 final_vlans_list.append(str(num))
#         else:
#             final_vlans_list.append(item.strip())
#     return final_vlans_list


def get_aci_leaf_port_status(dc: str, aci_pod: str, aci_node: str):
    apic_session = APIC(dc)
    initial_intf_data1 = apic_session.apic_get(f"node/class/topology/{aci_pod}/{aci_node}/l1PhysIf.json")['imdata']
    initial_intf_data2 = apic_session.apic_get(f"node/class/topology/{aci_pod}/{aci_node}/ethpmPhysIf.json")['imdata']
    initial_vlan_data = apic_session.apic_get(f"node/class/topology/{aci_pod}/{aci_node}/vlanCktEp.json")['imdata']
    # Get info about physical state of interfaces
    filtered_intf_data1 = list(map(get_intf_attributes1, initial_intf_data1))
    # Get info about logical state of interfaces (VLANs etc.)
    filtered_intf_data2 = list(map(get_intf_attributes2, initial_intf_data2))
    # Map internal VLANs retrieved via the above call to real VLANs
    mapped_vlans = get_real_vlans(initial_vlan_data)
    initial_intf_data = combine_intf_attributes(filtered_intf_data1, filtered_intf_data2)
    final_intf_data = []
    for intf_data in initial_intf_data:
        # Turn VLANs list from string like '10-11,14' into list like ['10', '11', '14']
        expanded_vlans = expand_vlans(intf_data['operVlans'])
        # Search expanded_vlans in mapped_vlans to get real VLANs
        real_vlans = []
        for vlan in expanded_vlans:
            if mapped_vlans.get(vlan):
                real_vlans.append(mapped_vlans.get(vlan))
        real_vlans.sort()
        # Change real_vlans from list to string, and swap internal VLANs with it
        real_vlans = ', '.join(real_vlans)
        intf_data['operVlans'] = real_vlans
        # Change native VLAN to real native VLAN
        intf_data['nativeVlan'] = mapped_vlans.get(intf_data['nativeVlan'].lstrip('vlan-'))
        final_intf_data.append(intf_data)
    return final_intf_data