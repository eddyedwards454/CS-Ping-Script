import os

ip_list = ['8.8.8.8']
for ip in ip_list:
    response = os.popen(f"ping {ip}").read()
    print(response)
    if "Received = 4" in response:
        print(f"UP {ip} Ping Successful")
    else:
        print(f"DOWN {ip} Ping Unsuccessful")

for ping in range(1,100):
   ip="192.168.10."+str(ping)
   response = os.system("ping -c 3 %s" % ip)
   print(response)