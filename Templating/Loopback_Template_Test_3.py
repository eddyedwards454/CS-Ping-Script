import yaml
from netmiko import Netmiko
from netmiko import ConnectHandler
from jinja2 import Environment, FileSystemLoader

hosts = yaml.load(open('hosts_3.yml'), Loader=yaml.SafeLoader)
interfaces = yaml.load(open('loopback_test_yaml_3.yml'), Loader=yaml.SafeLoader)
print(hosts)
# print(type(hosts))
# print(hosts['INTERNET'][0]['name'])
# print(test2)
# print(interfaces)
# print(interfaces['interfaces'])
# print(interfaces['interfaces'][0]['description'])

# # Loads the j2 template replaces interafces
env = Environment(loader = FileSystemLoader('.'), trim_blocks=True, autoescape=True)
template = env.get_template('Loopback_Template_Test_3.j2')
loopback_config = template.render(data2=interfaces)
print(loopback_config)

for host in hosts["INTERNET"]:
   net_connect = ConnectHandler(
      host = host["name"],
      username = host["username"],
      password = host["password"],
      port = host["port"],
      device_type = host["type"]
   )
   print(f"Logged into {host['name']} successfully")
   output = net_connect.send_config_set(loopback_config.split("\n"))


# for host in hosts["hosts"]:
#    net_connect = ConnectHandler(
#       host = host["name"],
#       username = host["username"],
#       password = host["password"],
#       port = host["port"],
#       device_type = host["type"]
#    )
#    print(f"Logged into {host['name']} successfully")
#    output = net_connect.send_config_set(loopback_config.split("\n"))
#
# # Used to save configuration
# answer2 = input("Do you want to backup the device now  ? (yes or no)\n\n\n ")
# if any(answer2.lower() == f for f in ["yes", 'y', '1', 'ye']):
#     print('You have chosen Yes !!!!\n')
#     print(' The system will now be backed up ')
#     for host in hosts["hosts"]:
#        net_connect = ConnectHandler(
#           host=host["name"],
#           username=host["username"],
#           password=host["password"],
#           port=host["port"],
#           device_type=host["type"]
#        )
#        print(f"Logged into {host['name']} successfully")
#        # below is a module that saves the configuration
#        output = net_connect.save_config()
#        # print(output)
#        print(f"Configuration saved of {host['name']} was successfully completed")
#        print(output)
# # #
#
#
#
#
# elif any(answer2.lower() == f for f in ['no', 'n', '0']):
#     print('You have chosen NO !!!!')
#     print('-------------------------------------------------------------')
#     print('-------------------------------------------------------------')
#     print('------PLEASE NOTE: Device as not been backed up !!!!------------')
#     print('-------------------------------------------------------------')



# BELOW NOT REQUIRED:
# for host in hosts["hosts"]:
#    net_connect = ConnectHandler(
#       host=host["name"],
#       username=host["username"],
#       password=host["password"],
#       port=host["port"],
#       device_type=host["type"]
#    )
#    print(f"Logged into {host['name']} successfully")
#    # below is a module that saves the configuration
#    output = net_connect.save_config()
#    # print(output)
#    print(f"Configuration saved of {host['name']} was successfully completed")
