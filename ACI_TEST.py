import requests

# Set the APIC IP address and credentials
apic_url = "https://192.168.100.10"
username = "admin"
password = "Jennygbmwx5!"

# Set the base URL for the ACI REST API
base_url = f"{apic_url}/api/"

# Set the headers for the HTTP request
headers = {
    "Content-Type": "application/json",
}

# Set the payload for the HTTP request
payload = {
    "aaaUser": {
        "attributes": {
            "name": username,
            "pwd": password,
        }
    }
}

# Send a POST request to the /aaaLogin endpoint to authenticate
response = requests.post(f"{base_url}aaaLogin", json=payload, headers=headers, verify=False)

# Get the token from the response
token = response.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]

# Set the headers for the next HTTP request with the token
headers["Cookie"] = f"APIC-Cookie={token}"

# Send a GET request to the /leaf/node/mo/uni/tn-<TENANT_NAME>/ap-<APPLICATION_PROFILE>/epg-<EPG_NAME>.json endpoint to get the list of leaf ports
response = requests.get(f"{base_url}leaf/node/mo/uni/tn-<TENANT_NAME>/ap-<APPLICATION_PROFILE>/epg-<EPG_NAME>.json", headers=headers, verify=False)

# Get the list of leaf ports from the response
leaf_ports = response.json()["imdata"]

# Print the list of leaf ports
print(leaf_ports)
