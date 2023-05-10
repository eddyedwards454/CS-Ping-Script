from netmiko import ConnectHandler
import getpass

passwd = getpass.getpass('Please enter the password: ')

my_devices = ['192.168.100.52', '192.168.100.144', '192.168.100.143'] #list of devices
device_list = list() #create an empty list to use it later

for device_ip in my_devices:
    device = {
        "device_type": "cisco_nxos",
        "host": device_ip,
        "username": "admin",
        "password": passwd, # Log in password from getpass
        "secret": passwd # Enable password from getpass
    }
    device_list.append(device)

print(device_list) #list of dictionaries
loopback = [] # last ocet for IP address
x = int(input("Type a number to start the range:"))
y = int(input("Type a number to end the range:"))
for i in range(x, y): # list of end ipaddress
    var = (i)
    print(var)
    loopback.append(var)

print(loopback)

for each_device in device_list:
    connection = ConnectHandler(**each_device)
    connection.enable()
    print(f'Connecting to {each_device["host"]}')
    for x in loopback:
        # print(x)
        inteface_loopback_no = 'no interface loopback  ' + str(x)
        ip_address = 'ip address 172.16.100.' + str(x) + '  255.255.255.255'
        print(inteface_loopback_no)
        print(ip_address)
        commands = (inteface_loopback_no), (ip_address)
        print(commands)
        output = connection.send_config_set(commands)
        print(output)

    print(f'Closing Connection on {each_device["host"]}')
    connection.disconnect()


