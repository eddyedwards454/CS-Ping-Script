from __future__ import print_function
from pprint import pprint
try:
    # PY2
    ip_addr = raw_input("Please enter an IP address: ")
except NameError:
    # PY3
    ip_addr = input("Please enter an IP address: ")

octets = ip_addr.split(".")
print()
print("{:^15}{:^15}{:^15}{:^15}".format("Octet1", "Octet2", "Octet3", "Octet4"))
print("-" * 60)
print("{:^15}{:^15}{:^15}{:^15}".format(*octets))
print("{:^15}{:^15}{:^15}{:^15}".format(bin(int(octets[0])), bin(int(octets[1])),
                                        bin(int(octets[2])), bin(int(octets[3]))))
print("{:^15}{:^15}{:^15}{:^15}".format(hex(int(octets[0])), hex(int(octets[1])),
                                        hex(int(octets[2])), hex(int(octets[3]))))
print("-" * 60)
print()


with open("show_arp.txt") as f:
    show_arp = f.readlines()
    print(show_arp)

# Remove header line
show_arp = show_arp[1:]
pprint(show_arp)

show_arp.sort()
# Grab only the first three entries
my_entries = show_arp[:3]
my_entries = '\n'.join(my_entries)

with open("arp_entries.txt", "wt") as f:
    f.write(my_entries)