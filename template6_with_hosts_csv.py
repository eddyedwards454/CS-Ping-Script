#!/usr/bin/env python3
import csv
import jinja2
import time
from netmiko import Netmiko
from netmiko import ConnectHandler

## Netmiko debugging
# import logging
#logging.basicConfig(filename='netmiko_output.log', level=logging.DEBUG)
#logger = logging.getLogger('netmiko')

csv_file = 'hosts.csv'
jinja_template = 'template6.j2'

inventory = {} # Overall working dictionary
inv_list = [] # This list will contain each device as a dictionary element


# Parse the CSV file
with open(csv_file) as f:
    read_csv = csv.DictReader(f)
    for vals in read_csv:
        # Read in all k/v's per row. I'm sure there's some real cool
        #  programmatic way to do this
        # These values must match the header row in the CSV file
        inventory['username'] = vals['username']
        inventory['password'] = vals['password']
        inventory['device_type'] = vals['device_type']
        inventory['device'] = vals['device']
        inventory['host'] = vals['host']
        inventory['port'] = vals['port']
        inventory['lo1ip'] = vals['lo1ip']
        inventory['ifg00ip'] = vals['ifg00ip']
        inventory['ifg01ip'] = vals['ifg01ip']
        inventory['ifg02ip'] = vals['ifg02ip']
        inventory['ifg00mask'] = vals['ifg00mask']
        inventory['ifg01mask'] = vals['ifg01mask']
        inventory['ifg02mask'] = vals['ifg02mask']

        # Build a list with each row as a dictionary element
        inv_list.append(inventory.copy())
        # print(inv_list)
        hosts = (inv_list)
        print(hosts)
        # print(inv_list)




        for items in inv_list:
            print('\nCurrent device: ' + items['device'])
        #     # Generate configuration lines with Jinja2
        #     hosts = inv_list
        with open('template6.j2') as f:
            tfile = f.read()
            # print(tfile)
            template = jinja2.Template(tfile)
        #     # # Convert each line into a list element for passing to Netmiko
            cfg_list = template.render(items).split('\n')
            print(cfg_list)



        for host in hosts:
            net_connect = ConnectHandler(
                host= host['host'],
                username=host["username"],
                password=host["password"],
                port=host["port"],
                device_type=host["device_type"]
            )
            print(f"Logged into {host['host']} successfully")
            output = net_connect.send_config_set(cfg_list)


# Generate the configurations and send it to the devices
# for items in inv_list:
#     print('\nCurrent device: ' + items['device'])
#      # Generate configuration lines with Jinja2
#     hosts = inv_list
#     with open(jinja_template) as f:
#         tfile = f.read()
#         print(tfile)
#     template = jinja2.Template(tfile)
#     # # Convert each line into a list element for passing to Netmiko
#     cfg_list = template.render(items).split('\n')
#     print(cfg_list)

    # # hostx = (cfg_list[0])
    # # print(hostx)
    # # w = open('template_config.txt', 'w')
    # # w.writelines((cfg_list) + '\n')
    # # w.close()

    # ssh = ConnectHandler(**hostx)
    # result = ssh.send_config_from_file('cfg_list')



