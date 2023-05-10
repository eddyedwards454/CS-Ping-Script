my_list_of_devices = ["R1", "R2", "R3", "CoreSwitch", "Access1"]
interface_list = ["interface g0/0", "interface g0/1", "interface g0/2", "interface g0/3"]

for device in my_list_of_devices:
    for interface in interface_list:
        print(f"I have {device} in my network and they have {interface_list} in them")


for interface in interface_list:
    print(f"interface{interface}\n ip ospf area 0\n")

print(f"I have {my_list_of_devices[0]} in my network and they have {interface_list} in them ")


test_string = "this is just a list of strings"

for string in test_string:
    print(string)