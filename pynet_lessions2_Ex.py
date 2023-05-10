from __future__ import print_function, unicode_literals

with open("show_ip_bgp_summ.txt") as f:
    bgp_summ = f.read()
    #print(bgp_summ)

bgp_summ = bgp_summ.splitlines()
#print(bgp_summ)
first_line = bgp_summ[0]
print(first_line)
as_number1 = first_line.split()
print(as_number1)
as_number = first_line.split()[-5]
print(as_number)
print(f"Local AS Number: " + (as_number))

last_line = bgp_summ[-1]
peer_ip = last_line.split()[0]
print("BGP Peer IP Address: {}".format(peer_ip))