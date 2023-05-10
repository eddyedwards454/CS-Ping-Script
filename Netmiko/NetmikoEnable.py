from netmiko import ConnectHandler
from getpass import getpass
username = input("What is the username you want to use   ")
password = getpass()
secret = getpass("Enter secret: ")



cisco1 = {
    "device_type": "cisco_ios",
    "host": "192.168.100.96",
    "username": username,
    "password": password,
    "secret": secret,
}
for device in (cisco1):
    net_connect = ConnectHandler(**cisco1)
    # Call 'enable()' method to elevate privileges
    net_connect.enable()
    print(net_connect.find_prompt())
    net_connect.disconnect()

