def expand_vlans(vlans_list):
    # Takes input like '10,11-13' and returns ['10', '11', '12', '13']
    final_vlans_list = []
    vlans_list = vlans_list.split(',')
    for item in vlans_list:
        if '-' in item:
            range_start, _, range_end = item.strip().partition('-')
            for num in range(int(range_start), int(range_end) + 1):
                final_vlans_list.append(str(num))
        else:
            final_vlans_list.append(item.strip())
    return final_vlans_list


expand_vlans(list)

list = ['14', '16', '18', '20']