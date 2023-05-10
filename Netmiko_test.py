import json

from netmiko import ConnectHandler

net_connect = ConnectHandler(
    device_type="cisco_xr",
    host="192.168.100.10",
    username="admin",
    password="Jennygbmwx5!",
)


print(net_connect.find_prompt())
# output = net_connect.send_command('moquery -c lldpAdjEp -f ""lldp.AdjEp.capability!""=""router"""')
# output = net_connect.send_command("moquery -c lldpAdjEp | grep  ""capability|dn""")
output = net_connect.send_command("moquery -c fabricSetupP | grep -E ""tepPool""") + ("moquery -c fabricSetupP | grep -E ""podId""")
print(output)
print(type(output))




# connect_to = {"device_type" :"cisco_xe",
#     "host":"192.168.100.10",
#     "username":"admin",
#     "password":"Jennygbmwx5!"
# }
# command = str("moquery -c lldpAdjEp -f ""lldp.AdjEp.capability!""=""router""")
# # command = str("moquery -c lldpAdjEp -f ""lldp.AdjEp.capability!""=""router"" and lldp.AdjEp.capability!="bridge,router"")

#
# with ConnectHandler(**connect_to) as net_connect:
#     output = net_connect.send_command(command, use_textfsm=True)
#     print(output)


# output = net_connect.send_command('moquery -c lldpAdjEp -f 'lldp.AdjEp.capability!="router" and lldp.AdjEp.capability!="bridge,router')
# output = net_connect.send_command('moquery -c lldpAdjEp -f ""lldp.AdjEp.capability!="router" and lldp.AdjEp.capability!="bridge,router""')
# output = net_connect.send_command(("moquery -c lldpAdjEp -f ""lldp.AdjEp.capability!""=""router""")
# print(output)