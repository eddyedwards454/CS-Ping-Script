
from jinja2 import Environment, FileSystemLoader
ENV = Environment(loader=FileSystemLoader('.'))
wayne = ENV.get_template('template5loop.j2')
import os
interface_dict = {
    "name": "GigabitEthernet0/1",
    "description": "Server Port",
    "vlan": 10,
    "uplink": False,
    "test": "this is a test"
}
interface_dict2 = {
    "name": "GigabitEthernet0/2",
    "description": "Access  Port",
    "vlan": 20,
    "uplink": True,
    "test": "this is a test"
}
# print(template.render(interface=interface_dict))

x = (wayne.render(interface=interface_dict2))
print(x)
if os.path.exists('template_config.txt'):
    os.remove('template_config.txt')
w = open('template_config.txt', 'w')
w.writelines(x)
w.close()
