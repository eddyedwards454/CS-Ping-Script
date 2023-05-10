with open("show_ip_int_brief.txt") as f:
    show_ip_int_brief = f.readlines()

fa4_ip = show_ip_int_brief[5].strip()
print(fa4_ip)
fields = fa4_ip.split()
print(fields)
intf = fields[0]
ip_address = fields[1]
upordown = fields[4]


my_results = (intf, ip_address, upordown)
my_results1 = my_results[0]
print(f" This interface is : " + (my_results1))