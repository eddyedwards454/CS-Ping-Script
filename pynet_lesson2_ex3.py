from __future__ import print_function, unicode_literals
from pprint import pprint

with open("show_arp.txt") as f:
    show_arp = f.readlines()

# Remove header line
show_arp = show_arp[1:]
pprint(show_arp)

show_arp.sort()
# Grab only the first three entries
my_entries = show_arp[:3]
my_entries = '\n'.join(my_entries)

with open("arp_entries.txt", "wt") as f:
    f.write(my_entries)