import yaml
from netmiko import Netmiko
from netmiko import ConnectHandler
from jinja2 import Environment, FileSystemLoader

hosts = yaml.load(open('hosts.yml'), Loader=yaml.SafeLoader)
interfaces = yaml.load(open('loopback_test_yaml_3.yml'), Loader=yaml.SafeLoader)


# print(hosts)
# Loads the j2 template replaces interafces
env = Environment(loader = FileSystemLoader('.'), trim_blocks=True, autoescape=True)
template = env.get_template('Loopback_Template_Test_3.j2')
loopback_config = template.render(data2=interfaces)
print(loopback_config)

for host in hosts["hosts"]:
   net_connect = ConnectHandler(
      host = host["name"],
      username = host["username"],
      password = host["password"],
      port = host["port"],
      device_type = host["type"]
   )
   print(f"Logged into {host['name']} successfully")
   output = net_connect.send_config_set(loopback_config.split("\n"))

# Used to save configuration


for host in hosts["hosts"]:
   net_connect = ConnectHandler(
      host=host["name"],
      username=host["username"],
      password=host["password"],
      port=host["port"],
      device_type=host["type"]
   )
   print(f"Logged into {host['name']} successfully")
   # below is a module that saves the configuration
   output = net_connect.save_config()
   # print(output)
   print(f"Configuration saved of {host['name']} was successfully completed")
