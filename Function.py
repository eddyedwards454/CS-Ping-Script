

def vendorx(some_var):
    print(some_var)

vendors = ['aritsa','junipter','big_switch','cisco']

# wayne / jen can be anything
def get_commands(wayne, jen):
    commands = []
    commands.append('vlan' + wayne)
    commands.append('name' + jen)
    return commands

def push_commands(device, commands):
    print('Connecting to device:' + device)
    for cmd in commands:
        print('Sending command: ' + cmd)

devices =['switch1','switch2','switch3']

vlans = [{'id': '10','name': 'USERS'}, {'id': '20','name': 'VOICE'}, {'id': '30','name': 'WLAN'}, {'id': '40','name': 'DLAN'}]

for vlan in vlans:
    id = vlan.get('id')
    name = vlan.get('name') #
    print('\n')
    print('CONFIGURING VLAN:' + id)
    commands = get_commands(id, name)#id is wayne , name is jen in the function get_commands at the start of the script
    print(commands)
    for device in devices:
        push_commands(device, commands)#calling the function above
        # print('/n')


