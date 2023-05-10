from netmiko import ConnectHandler
#As mentioned you have a list of devices
ip_list=["192.168.100.10","192.168.100.15"]#put all ip addresses in this list
u_name="admin"
pwd="Jennygbmwx5!"
#Run a for loop to access each device
for ip in ip_list:
    cred={'device_type':'cisco_ios',
        'ip':ip,
        'username':u_name,
        'password':pwd}
    net_connect=ConnectHandler(**cred)
    print("Login Successful")
    output=net_connect.send_command('acidiag fnvread"')
    print(output)
