
from netmiko import ConnectHandler
# from getpass import getpass
#
# password = getpass()

cisco1 = {
    "device_type": "cisco_ios",
    "host": "192.168.100.141",
    "username": "admin",
    "password": "cisco",
    "secret": "cisco",
}
cisco2 = {
    "device_type": "cisco_ios",
    "host": "192.168.100.140",
    "username": "admin",
    "password": "Jennygbmw5!",
    "secret": "cisco",
}
nxos1 = {
    "device_type": "cisco_ios",
    "host": "192.168.100.10",
    "username": "admin",
    "password": "Jennygbmwx5!",
}

nxos2 = {
    "device_type": "cisco_ios",
    "host": "192.168.100.15",
    "username": "admin",
    "password": "Jennygbmwx5!",
}
nxos3 = {
    "device_type": "cisco_ios",
    "host": "192.168.100.98",
    "username": "admin",
    "password": "cisco",
}
command = "moquery -c lldpAdjEp -f 'lldp.AdjEp.capability!=""router"" and lldp.AdjEp.capability!=""bridge,router""'"
command2 = "moquery -c lldpAdjEp"

for device in (nxos1, nxos2):
    net_connect = ConnectHandler(**device)
    with ConnectHandler(**device) as net_connect:
        output = net_connect.send_command(command)
        # file1 = open('vlan.txt', 'a')
        file1 = open('C://SCRIPTS//Learning Home Work//netmiko//vlan.txt', 'a')
        file1.write(output)
        print(output)
        # with open("vlanwayne.txt", "w") as f:
        #     f.write(output)

    net_connect.disconnect()

# with open("vlanwayne.txt") as f:
#     vlanoutput = f.read()
#     #print(vlanoutput)
#
#
# # for device1 in (cisco1, cisco2):
#     net_connect = ConnectHandler(**device1)
#     print(net_connect.find_prompt())
#     with ConnectHandler(**device1) as net_connect:
#         output = net_connect.send_command(command2)
#         print(output)
#     net_connect.disconnect()
#
#
#
# connection = ConnectHandler(**cisco1)
# connection.enable()
# config_commands = ["interface loopback 0 " "description WAN", "no shutdown", "exit"]
# connection.send_config_set(config_commands)
# print('Closing Connection')
# connection.disconnect()


