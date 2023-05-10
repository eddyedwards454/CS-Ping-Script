import os
import csv
from xlsxwriter.workbook import Workbook


# Verifies your os type
OS_TYPE = os.name
# Sets the count modifier to the os type
count = '-n' if OS_TYPE == 'nt' else '-c'

def create_ip_list():
    """Creates an ip address list
        return: Return the ip_list
        rtype: list
    """
    ip_list = []
    with open("ip_file.txt", "r") as file:
        for line in file:
            ip_list.append(line.strip())
    return ip_list

def ping_device_after(ip_list):
    """Ping ip_list and return results
        return: None
        rtype: None
    """
    results_file_post = open("results_post.txt", "w+")
    for ip in ip_list:
        response = os.popen(f"ping {ip} {count} 1").read()
        if "Received = 1" and "Approximate" in response:
            print(f"UP {ip} Ping Successful")
            results_file_post.write(f"UP,{ip},Ping Successful," + "\n")
        else:
            print(f"Down {ip} Ping Unsuccessful")
            results_file_post.write(f"Down,{ip},Ping Unsuccessful," + "\n")
    results_file_post.close()
    print("File as now completed see Results_post.txt for output")


def Compare():
    f1 = open("results.txt", "r")
    f2 = open("results_post.txt", "r")


    i = 0

    ipList = []
    ipList.append('Pre Eth:,Pre IP:,Pre Status:,Post Eth:,Post IP:,Post Status:,Comments:')
    f = open("compare_file_final.csv", "w")

    for Pre_IP_address in f1:
        i += 1
