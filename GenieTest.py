from getpass import getpass
from pprint import pprint
from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios",
    "host": "192.168.100.52",
    "username": "admin",
    "password": getpass()
}

with ConnectHandler(**device) as net_connect:
    output = net_connect.send_command("show ip interface brief", use_genie=True)

print()
pprint(output)
print()