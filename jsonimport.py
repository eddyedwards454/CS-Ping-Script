import dataclasses
import json

# with open('tenant.txt') as f:
#     data = f.read()
#
# json_dict = json.loads(data)
# print('The json loaded in here is loaded as type {0}\n'.format(type(json_dict)))
# print(json_dict)
# x = json_dict['totalCount']
# print(x)
# y = json_dict['imdata']
# print(y)
#
# w = y[0]['fvTenant']['attributes']['dn']
# print(w)
# print(type(w))
# print('This is the tenant:\n' + str(w))


with open('Interfaces.txt') as f:
    data = f.read()

json_dict = json.loads(data)
# print('The json loaded in here is loaded as type {0}\n'.format(type(json_dict)))
print(json_dict)
# NunberOf = json_dict[0]
# print(NunberOf)
x = int(json_dict['totalCount']) # Truns string into Int
print(x) # This prints the number of items
print(type(x))

#
# loopback = []
# # r = 0
# # for i in range(r, x):  # list of end ipaddress
# #     var = (i)
# #     # print('You are deleting the following loopbacks:' + str(var))
# #     loopback.append(var)
# #     # print(loopback)
# # for s in loopback:
# #     print(s)


#This works to get the DN
y = json_dict['imdata']
print(y)
print(len(y))
w = y[0]['l1PhysIf']['attributes']['dn']
print(w)
x = y[1]['l1PhysIf']['attributes']['dn']
print(x)

# for char in w:
#     if char in "/":
#         x.replace(char,"")
#         print(char)