from netmiko import ConnectHandler
from getpass import getpass

net_connect = ConnectHandler(
    device_type="cisco_ios",
    host="192.168.100.52",
    username="admin",
    password="cisco"
)


print(net_connect.find_prompt())
net_connect.disconnect()