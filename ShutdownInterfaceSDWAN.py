from typing import List, Dict

from netmiko import ConnectHandler
import getpass

my_devices = ['192.168.100.94','192.168.100.95']  # list of devices
passwd = getpass.getpass('Please enter the password: \n')
device_list = list()
print(my_devices)
# for device in my_devices:
#     device_ip = {
#         "device_type": "cisco_nxos",
#         "host": device_ip,
#         "username": "admin",
#         "password": "cisco",  # Log in password from getpass
#         "secret": "cisco",  # Enable password from getpass
#     }
#     device_list.append(device)
#     print(device_list)

