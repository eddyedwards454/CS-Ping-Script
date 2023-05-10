import re
import sys
import os
from io import StringIO
from netmiko import ConnectHandler
import getpass

# w = input('What is the IP of the device you want to connected too, in the format x.x.x.x ? \n')
# print(w)
#
# my_devices = []
# my_devices.append(w)
# print(my_devices)
passwd = getpass.getpass('Please enter the password: \n')
#
# my_devices = ['192.168.100.52', '192.168.100.144', '192.168.100.143'] #list of devices
# device_list = list()  # create an empty list to use it later

with open("IP.txt") as file:
   my_devices = file.readlines()
   print(my_devices)

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
    print(device_list)

answer2 = input("Do you want to backup the device now  ? (yes or no)\n\n\n ")
if os.path.exists('OUTPUTFROMBACKUP.txt'):
    os.remove('OUTPUTFROMBACKUP.txt')
else:
    w = open('OUTPUTFROMBACKUP.txt', 'w')



if any(answer2.lower() == f for f in ["yes", 'y', '1', 'ye']):
    print('You have chosen Yes !!!!\n')
    # print(f'You are about to back up the following devices\n') + str(device_list)
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
        print('Now finshed adding Loopbacks and saving the configuration thank you ! We are saving the output to a file \n  ')
        print('Saving output to file called OUTPUTFROMBACKUP.txt')
        # for each_device1 in device_list:
        #     print(each_device1)
        #     w = open('OUTPUTFROMBACKUP.txt', 'a')
        #     w.write(output)
        #     w.write(outout2)
        #     # # sys.stdout.close()


        w = open('OUTPUTFROMBACKUP.txt', 'a')
        print(my_devices)
        # w.write(output)
        w.write(outout2)
        # sys.stdout.close()


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