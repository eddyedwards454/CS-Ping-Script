from fastapi import APIRouter, Request, Response
from db.connection import retrieve_from_db

aci_leafs_per_region_and_dc_router = APIRouter()

@aci_leafs_per_region_and_dc_router.get("/aci/leafs-per-region-and-dc")
async def aci_leafs_per_region_and_dc(request: Request, response: Response):
    #
    # Initialize response object
    ACI_leafs = {
        'AMER': {},
        'APAC': {},
        'EMEA': {}
    }
    #
    # Get a list of sites with ACI deployment - per region
    # Response sample: [{'DC': 'SLO'}, {'DC': 'GSH'}]
    AMER_ACI_DCs = retrieve_from_db("SELECT DISTINCT UPPER(SUBSTRING(Hostname, 1, 3)) AS 'DC' FROM zabbix_devices WHERE v2_device_type = 'Cisco APIC' AND Region = 'AMER'")
    APAC_ACI_DCs = retrieve_from_db("SELECT DISTINCT UPPER(SUBSTRING(Hostname, 1, 3)) AS 'DC' FROM zabbix_devices WHERE v2_device_type = 'Cisco APIC' AND Region = 'APAC'")
    EMEA_ACI_DCs = retrieve_from_db("SELECT DISTINCT UPPER(SUBSTRING(Hostname, 1, 3)) AS 'DC' FROM zabbix_devices WHERE v2_device_type = 'Cisco APIC' AND Region = 'EMEA'")
    #
    # Add site names as per-region keys inside the final response object
    for item in AMER_ACI_DCs:
        ACI_leafs['AMER'][item['DC']] = []
    for item in APAC_ACI_DCs:
        ACI_leafs['APAC'][item['DC']] = []
    for item in EMEA_ACI_DCs:
        ACI_leafs['EMEA'][item['DC']] = []
    #
    # Get a list of ACI leafs per site
    # Response sample: [{'site': 'CDC', 'switch': 'cdcsl0113.link.hedani.net'}, {'site': 'CDC', 'switch': 'cdcsl0114.link.hedani.net'}]
    AMER_ACI_leafs = retrieve_from_db(
        """
        SELECT
        	UPPER(SUBSTRING(Hostname, 1, 3)) AS site, 
        	SUBSTRING(Hostname, 1, 9) as switch
        FROM
        	zabbix_devices
        WHERE
        	v2_device_type = 'Cisco ACI Node'
        	AND Capability != 'Closed Branch'
        	AND SUBSTRING(Hostname, 4, 2) != 'sp'
        	AND SUBSTRING(Hostname, 4, 2) != 'bl'
        	AND Region = 'AMER'
        ORDER BY
        	Hostname ASC
        """
    )
    APAC_ACI_leafs = retrieve_from_db(
        """
        SELECT
        	UPPER(SUBSTRING(Hostname, 1, 3)) AS site, 
        	SUBSTRING(Hostname, 1, 9) as switch
        FROM
        	zabbix_devices
        WHERE
        	v2_device_type = 'Cisco ACI Node'
        	AND Capability != 'Closed Branch'
        	AND SUBSTRING(Hostname, 4, 2) != 'sp'
        	AND SUBSTRING(Hostname, 4, 2) != 'bl'
        	AND Region = 'APAC'
        ORDER BY
        	Hostname ASC
        """
    )
    EMEA_ACI_leafs = retrieve_from_db(
        """
        SELECT
        	UPPER(SUBSTRING(Hostname, 1, 3)) AS site, 
        	SUBSTRING(Hostname, 1, 9) as switch
        FROM
        	zabbix_devices
        WHERE
        	v2_device_type = 'Cisco ACI Node'
        	AND Capability != 'Closed Branch'
        	AND SUBSTRING(Hostname, 4, 2) != 'sp'
        	AND SUBSTRING(Hostname, 4, 2) != 'bl'
        	AND Region = 'EMEA'
        ORDER BY
        	Hostname ASC
        """
    )
    #
    # Add leaf names into (empty) site lists inside the final response object
    for item in AMER_ACI_leafs:
        ACI_leafs['AMER'][item['site']].append(item['switch'])
    for item in APAC_ACI_leafs:
        ACI_leafs['APAC'][item['site']].append(item['switch'])
    for item in EMEA_ACI_leafs:
        ACI_leafs['EMEA'][item['site']].append(item['switch'])
    #print(ACI_leafs)

    return ACI_leafs