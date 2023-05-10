from netmiko import ConnectHandler
import getpass

w = input('What is the IP in the format x.x.x.x')
print(w)

my_devices = []
my_devices.append(w)
print(my_devices)
passwd = getpass.getpass('Please enter the password: ')

# # my_devices = ['192.168.100.52', '192.168.100.144', '192.168.100.143'] #list of devices
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

# print(device_list) #list of dictionaries
loopback = [] # last ocet for IP address
x = int(input("Type a number Loopback Interface to start with :"))
y = int(input("Type a number Loopback Interface to end with NOTE The actual number of Interfaces created will be one less than this number :"))
for i in range(x, y): # list of end ipaddress
    var = (i)
    print(var)
    loopback.append(var)

# print(loopback)
z = 15

for each_device in device_list:
    z += 1
    connection = ConnectHandler(**each_device)
    connection.enable()
    print(f'Connecting to {each_device["host"]}')
    for x in loopback:
        # print(x)
        inteface_loopback_no = 'interface loopback  ' + str(x)
        ip_address = 'ip address 172.' + str(z) +'.100.' + str(x) + '  255.255.255.255'
        eigrp = 'ip router eigrp CORE'
        # print(inteface_loopback_no)
        # print(ip_address)
        commands = (inteface_loopback_no), (ip_address), (eigrp)
        print(commands)
        output = connection.send_config_set(commands)
        print(output)

    print(f'Closing Connection on {each_device["host"]}')
    connection.disconnect()

for each_device1 in device_list:
    connection = ConnectHandler(**each_device1)
    connection.enable()
    print(f'Connecting to {each_device1["host"]}')
    commands1 = 'copy run startup'
    commands2 = 'show ip interface brief'
    output = connection.send_command(commands1)
    outout2 = connection.send_command(commands2)
    print(output)
    print(outout2)
    print('Now finshed adding Loopbacks and saving the configuration  ')
    # print('These are the new interafces that have been added'/n + (outout2))