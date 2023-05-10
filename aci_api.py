from db.external.direct_connection import retrieve_from_db, RetrieveError
from config_loader import ANSIBLE_RO_USER, ANSIBLE_RO_PASS
import requests


class APICError(Exception):
    pass


class APIC:
    def __init__(self, site):
        self.site = site
        self.user = ANSIBLE_RO_USER
        self.password = ANSIBLE_RO_PASS
        self.base_url = self._set_base_url()
        self.token = self._login()
        self.headers = {
            "Cookie": self.token
        }
    def _set_base_url(self):
        query = "SELECT DISTINCT UPPER(SUBSTRING(Hostname, 1, 3)) AS 'Site', Hostname FROM zabbix_devices " \
 \
                "WHERE v2_device_type = 'Cisco APIC' AND Hostname NOT LIKE '%%cimc%%' ORDER BY Hostname ASC"
    try:
        apic_hosts = retrieve_from_db(query)
    except RetrieveError:
        raise APICError(f"Could not find APIC Host for {self.site} site, DB query failed.")
    for h in apic_hosts:
        if h['Site'] == self.site:
            return f"https://{h['Hostname']}/api"
    raise APICError(f"Could not find APIC Host for {self.site} site")


def _login(self):
    login_url = f'{self.base_url}/aaaLogin.json'
    response = requests.post(login_url, verify=False, json={
        "aaaUser": {
            "attributes": {
                "name": self.user,
                "pwd": self.password
            }
        }
    })
    if response.status_code != 200:
        raise APICError(f"Could not log in to {self.base_url}")
    try:
        token = response.json()['imdata'][0]['aaaLogin']['attributes']['token']
    except (KeyError, IndexError):
        raise APICError(f"Could not receive APIC token")
    return f'APIC-Cookie={token}'


def apic_post(self, sub_path, payload):
    url = f"{self.base_url}/{sub_path.lstrip('/')}"
    response = requests.post(url, headers=self.headers, json=payload, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        raise APICError(f"POST {url} - {payload} request to APIC failed, code: "
                        f"{response.status_code} msg: {response.text}")
def apic_get(self, sub_path):
    url = f"{self.base_url}/{sub_path.lstrip('/')}"
    response = requests.get(url, headers=self.headers, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        raise APICError(f"GET {url} -request to APIC failed, code: "
                        f"{response.status_code} msg: {response.text}")