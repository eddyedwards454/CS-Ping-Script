import csv
from jinja2 import Template

template_file = "Template_Test_4.j2"

config_items = {
    "hostname": "HQ-SWITCH-01",
    "domain_name": "packet.net",
    "management_ip": "10.10.25.10 255.255.255.0",
    "next_hop": "10.10.25.1",
    "ntp_01": "192.168.10.1",
    "ntp_02": "192.168.20.1",
    "snmp_community": "s3creT",
    "device_location": "london-hq",
    "snmp_traps": ["license", "cpu threshold", "envmon", "errdisable"],
    "vlans": [
        {
            "name": "isp-01",
            "id": 10
        },
        {
            "name": "isp-02",
            "id": 11
        }
    ],
    "access_lists": [
        {
            "remark": "HQ-USERS",
            "acl": "10.25.0.0 0.0.255.255"
        },
        {
            "remark": "DC-SERVER-01",
            "acl": "10.12.25.21 0.0.0.0"
        },
        {
            "remark": "DC-SERVER-02",
            "acl": "10.12.32.21 0.0.0.0"
        },
        {
            "remark": "NMS",
            "acl": "10.12.32.10 0.0.0.0"
        }
    ],
    "interfaces": [
        {
            "name": "Gi 1/0/1",
            "description": "firewall-01-uplink",
            "port_type": 'trunk',
            "allowed_vlan": "10-11"

        },
        {
            "name": "Gi 1/0/2",
            "description": "firewall-02-uplink",
            "port_type": 'trunk',
            "allowed_vlan": "10-11"

        },
        {
            "name": "Gi 1/0/11",
            "description": "link-to-isp-01",
            "port_type": "access",
            "vlan": 10
        },
        {
            "name": "Gi 1/0/12",
            "description": "link-to-isp-02",
            "port_type": "access",
            "vlan": 11
        }
    ]
}

with open(template_file) as f:
    cisco_template = Template(f.read(), keep_trailing_newline=True)

cisco_config = cisco_template.render(config_items)
print(cisco_config)