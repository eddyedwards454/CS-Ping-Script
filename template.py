from jinja2 import Environment, FileSystemLoader
ENV = Environment(loader=FileSystemLoader('.'))
template = ENV.get_template('template.j2')
import os
interface_dict = {
    "name": "GigabitEthernet0/1",
    "description": "Server Port",
    "vlan": 10
}
interface_dict2 = {"name": "GigabitEthernet0/2", "description": "Access Port", "vlan": 20}





#     {
#     {"name": "GigabitEthernet0/2",
#     "description": "Access Port",
#     "vlan": 10},
#     {"name": "GigabitEthernet0/3",
#     "description": "Access Port",
#     "vlan": 20
#     },
# }




x = (template.render(interface=interface_dict2))
print(x)
print(type(x))


if os.path.exists('template_config.txt'):
    os.remove('template_config.txt')
w = open('template_config.txt', 'w')
w.writelines(x)
w.close()

