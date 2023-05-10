
from netmiko import ConnectHandler
from getpass import getpass

password = getpass()

cisco1 = {
    "device_type": "cisco_ios",
    "host": "192.168.100.141",
    "username": "admin",
    "password": password,
    "secret": "cisco",
}
cisco2 = {
    "device_type": "cisco_ios",
    "host": "192.168.100.140",
    "username": "admin",
    "password": password,
    "secret": "cisco",
}
nxos1 = {
    "device_type": "cisco_nxos",
    "host": "192.168.100.52",
    "username": "admin",
    "password": password,
}

nxos2 = {
    "device_type": "cisco_nxos",
    "host": "192.168.100.144",
    "username": "admin",
    "password": password,
}
nxos3 = {
    "device_type": "cisco_nxos",
    "host": "192.168.100.143",
    "username": "admin",
    "password": password,
}
command = "show vlan"


for device in (nxos1, nxos2, nxos3):
    net_connect = ConnectHandler(**device)
    with ConnectHandler(**device) as net_connect:
        output = net_connect.send_command(command)
        file1 = open('vlan.txt', 'a')
        file1.write(output)
        print( )
    net_connect.disconnect()
print(f"Vlan Txt as finshed")

vlan_file = open('vlan.txt', 'r')
vlans_text = vlan_file.read()
vlan_list = vlans_text.splitlines()
res = []
for ele in vlan_list:
    j = ele.replace('', '')
    res.append(j)
    print(res)
# vlan_list.str
print(vlan_list)
vlan_file.close()
file2 = open('vlan.txt', 'a')
file2.writelines(vlan_list)
file2.close()

# print(strip_vlan_list)
# vlans = []
#
# for item in vlan_list:


# with open("vlan.txt") as f:
#     vlanoutput = f.readlines()
#     print(vlanoutput)
#     print(vlanoutput[3:20])
