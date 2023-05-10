from APIC_login4 import get_token

aci_devices = ["192.168.100.10","192.168.100.15"]

for aci in aci_devices:
    print("This is the device you are logging into" + aci)
    token = get_token(aci)
# token = get_token(aci)
    print("The APIC token for " + aci + " is : " + token)


