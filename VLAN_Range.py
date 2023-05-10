w = open('C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output_Test.csv', 'w')
w.writelines('APIC,Pod,Node,Port,Adminstate,Native_vlan,Encap-VLAN'+ '\n')
w.close()
for encap_heading in range(1,25):
    vlan = 'Vlan' + str(encap_heading)
    a = open('C://SCRIPTS//SCRIPTS//Python Scripts//Learning Home Work//ACI Inventory//ACI_Node_Output_Test.csv', 'a')
    a.write('Encap_Vlan' + vlan)
    a.close()
