from netmiko import ConnectHandler

# cisco_router = {
#     'device_type': 'cisco_ios',
#     'host': '192.168.100.96',
#     'port': 22,
#     'username': 'admin',
#     'password': 'cisco',
# }
#
# ssh = ConnectHandler(**cisco_router)
#
# result = ssh.send_command('show run')
#
# print(result)
switch = {
    'device_type': 'cisco_nxos',
    'host':   '192.168.100.10',
    'username': 'admin',
    'password': 'Jennygbmwx5!',
    'port' : 22,          # optional, defaults to 22
    'secret': 'admin',     # optional, defaults to ''
    'session_log': 'log.log'    #generate a log session for the code to teshoot the code
}

try:        #Avoid Timeout & Auth errors and continuo for next switch
    net_connect = ConnectHandler(**switch)
except (NetMikoTimeoutException, NetMikoAuthenticationException):
    print ('\n' + 'Cannot connect to device: ' + host_ip)
    sys.exit()

host_list.append('192.168.100.10')      #Register IPs of connected hosts

timestamp = date.today()
#timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")       #Time including hours, minutes, seconds

hostname = net_connect.find_prompt()[:-1]   #Get the hostname

print ("Checking current status of ACI fabric ports for " + hostname + "_" + (host_ip))

command1 = "show switch"
#with ConnectHandler(**cisco1) as net_connect:
output1 = net_connect.send_command(command1)
node_list = re.findall(r"(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", output1, re.MULTILINE)


