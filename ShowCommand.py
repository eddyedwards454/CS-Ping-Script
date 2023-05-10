from netmiko import ConnectHandler
from getpass import getpass
from pprint import pprint
#username = input("What is the username you want to use   ")
password = getpass()
#secret = getpass("Enter secret: ")




cisco1 = {
    "device_type": "cisco_ios",
    "host": "192.168.100.144",
    "username": "admin",
    "password": password,
    #"secret": secret,
}

command = "show vlan"

with ConnectHandler(**cisco1) as net_connect:
    output = net_connect.send_command(command)

with ConnectHandler(**cisco1) as net_connect:
    # Use TextFSM to retrieve structured data
    output = net_connect.send_command(command, use_textfsm=True)

# print()
print(output)
# print()
VLAN = (output[1])
print(VLAN)
# print(type(VLAN))
print(f"This is the vlan you are looking for is  {VLAN['vlan_id']}")
print(VLAN.values())


