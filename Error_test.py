
aci = '192.168.100.10'
for Pod in range(1, 2):
    # for Pod in (1):

    # Loop through Nodes 1-15 (Really <Pod>01 - <Pod>15
    for NodeNum in range(1, 3):
        # Create Real ACI Node Number from Pod and NodeNum (Pad to 2 chars)
        ACI_node = f'{Pod}{NodeNum:02}
        print("APIC: " + aci + " - Pod: " + str(Pod) + " - Node: " + str(ACI_node))



