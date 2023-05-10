from fastapi import APIRouter, Request, Response
from db.connection import retrieve_from_db
from utils.on_demand.ACI import APIC_login
from utils.on_demand.API_calls import api_call_get

# Set initial header (token will be added later)
headers_aci = {'Content-Type': 'application/json', 'Accept': 'application/json'}

aci_leaf_port_status_router = APIRouter()

# Helper functions
def get_intf_attributes1(initial_intf_data):
    return initial_intf_data['l1PhysIf']['attributes']
#
def get_intf_attributes2(initial_intf_data):
    return initial_intf_data['ethpmPhysIf']['attributes']
#
def combine_intf_attributes(data1, data2):
    final_data = []
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
        final_data.append(inner_dict)
    return final_data

@aci_leaf_port_status_router.get("/aci/leaf-port-status")
async def aci_leaf_port_status(request: Request, response: Response):
    print(request.headers['dc'])
    #
    # Get a list of APICs per region
    APICs = retrieve_from_db("SELECT DISTINCT UPPER(SUBSTRING(Hostname, 1, 3)) AS 'Site', Hostname FROM zabbix_devices WHERE v2_device_type = 'Cisco APIC' AND Hostname NOT LIKE '%cimc%' ORDER BY Hostname ASC")
    #
    # Pick an APIC controller from the list depending on site in HTTP request
    APIC_FQDN = ''
    for item in APICs:
        if item['Site'] == request.headers['dc']:
            APIC_FQDN = item['Hostname']
            break
    #
    # Derive ACI pod and node numbers from switch name
    ACI_pod = 'pod-' + request.headers['switch'][6]
    ACI_node = 'node-' + request.headers['switch'][6:9]
    #
    # Construct URLs for API call
    url1 = f'https://{APIC_FQDN}/api/node/class/topology/{ACI_pod}/{ACI_node}/l1PhysIf.json'
    url2 = f'https://{APIC_FQDN}/api/node/class/topology/{ACI_pod}/{ACI_node}/ethpmPhysIf.json'
    #
    # Login to APIC and retrieve interface info
    token = APIC_login.login_APIC(f'{APIC_FQDN}')
    headers_aci['Cookie'] = token
    initial_data1 = api_call_get(url=url1, headers=headers_aci)['imdata']
    filtered_data1 = list(map(get_intf_attributes1, initial_data1))
    initial_data2 = api_call_get(url=url2, headers=headers_aci)['imdata']
    filtered_data2 = list(map(get_intf_attributes2, initial_data2))
    #
    return combine_intf_attributes(filtered_data1, filtered_data2)