import re
import sys

from netmiko import ConnectHandler
import getpass

w = input('What is the IP of the device you want to connected too, in the format x.x.x.x ? \n')
print(w)

my_devices = []
my_devices.append(w)
print(my_devices)
passwd = getpass.getpass('Please enter the password: \n')

# # my_devices = ['192.168.100.52', '192.168.100.144', '192.168.100.143'] #list of devices
device_list = list()  # create an empty list to use it later

for device_ip in my_devices:
    device = {
        "device_type": "cisco_nxos",
        "host": device_ip,
        "username": "admin",
        "password": passwd,  # Log in password from getpass
        "secret": passwd  # Enable password from getpass
    }
    device_list.append(device)

z = 15
answer = input("Is this to add or delete an interface ? (please use add or delete )")
if any(answer.lower() == f for f in ["add", 'ad', '1', 'yes', 'ye','Yes']):
    print("Adding Interface")
    loopback = []  # last ocet for IP address
    x = int(input("Type a number Loopback Interface to start with :"))
    if (x) > 999:
        print('\n\n      Error you can not have more than 999 Interfaces  - GOOD BYE !!!:  ')
        sys.exit()
    else:
        print(x)
    y = int(input(
        "Type a number Loopback Interface to end with NOTE The actual number of Interfaces created will be one less than this number: MAX 254"))
    if (y) > 255:
        print('\n\n      Error you can not have more than 254 Interfaces  - GOOD BYE !!!:  ')
        sys.exit()
    else:
        print(y)

    for i in range(x, y):  # list of end ipaddress
        var = (i)
        print('You are adding the following loopbacks:'+ str(var))
        loopback.append(var)
    for each_device in device_list:
        z += 1
        connection = ConnectHandler(**each_device)
        connection.enable()
        print(f'Connecting to {each_device["host"]}')
        for x in loopback:
            # print(x)
            inteface_loopback_no = 'interface loopback  ' + str(x)
            ip_address = 'ip address 172.' + str(z) + '.100.' + str(x) + '  255.255.255.255'
            eigrp = 'ip router eigrp CORE'
            # print(inteface_loopback_no)
            # print(ip_address)
            commands = (inteface_loopback_no), (ip_address), (eigrp)
            print(commands)
            output = connection.send_config_set(commands)
            print(output)

        print(f'Closing Connection on {each_device["host"]}')
        connection.disconnect()
        break

elif any(answer.lower() == f for f in ['delete', 'd', '0','no', 'No','del']):
    print('Deleting Interfaces')
    loopback = []  # last ocet for IP address
    x = int(input("Type a number Loopback Interface to start with :"))
    y = int(input(
        "Type a number Loopback Interface to end with NOTE The actual number of Interfaces created will be one less than this number :"))
    for i in range(x, y):  # list of end ipaddress
        print(i)
        var = (i)
        print('You are deleting the following loopbacks:'+ str(var))
        loopback.append(var)
    for each_device in device_list:
        z += 1
        connection = ConnectHandler(**each_device)
        connection.enable()
        print(f'Connecting to {each_device["host"]}')
        for x in loopback:
            # print(x)
            inteface_loopback_no = 'no interface loopback  ' + str(x)
            ip_address = 'ip address 172.' + str(z) + '.100.' + str(x) + '  255.255.255.255'
            eigrp = 'ip router eigrp CORE'
            # print(inteface_loopback_no)
            # print(ip_address)
            commands = (inteface_loopback_no), (ip_address), (eigrp)
            print(commands)
            output = connection.send_config_set(commands)
            print(output)

        print(f'Closing Connection on {each_device["host"]}')
        connection.disconnect()
        break
    # else:
    # i += 1
    # if i < 2:
    #     print('Please enter yes or no')
    # else:
    #     print('Nothing done')
else:
    i += 1
    if i < 2:
        print('Please enter yes or no')
    else:
        print('Nothing done')

answer2 = input("Do you want to backup the device now  ? (yes or no)\n\n\n ")
if any(answer2.lower() == f for f in ["yes", 'y', '1', 'ye']):
    print('You have chosen Yes !!!!\n')
    print(' The system will now be backed up and display all interfaces including the ones you have added/subtracted ')
    for each_device1 in device_list:
        connection = ConnectHandler(**each_device1)
        connection.enable()
        print(f'Connecting to {each_device1["host"]}')
        commands1 = 'copy run startup'
        commands2 = 'show ip interface brief'
        output = connection.send_command(commands1)
        outout2 = connection.send_command(commands2)
        print(f'Backing up Device Confiuration \n\n' + (output))
        print('Back up as now fully completed !\n')
        print(f'Current Interafaces Shown Below \n' + (outout2))
        print('Now finshed adding Loopbacks and saving the configuration thank you !  ')

elif any(answer2.lower() == f for f in ['no', 'n', '0']):
    print('You have chosen NO !!!!')
    print('-------------------------------------------------------------')
    print('-------------------------------------------------------------')
    print('------PLEASE NOTE: Device as not been backed up !!!!------------')
    print('-------------------------------------------------------------')


else:
    i += 1
    if i < 2:
        print('Please enter yes or no')
    else:
        print('Nothing done')