# Import json module
import json

# Define json data
customerData ="""{
    "id": "3425678",
    "name": "John Micheal",
    "email": "john@gmail.com",
    "type": "regular",
    "address": "4258 Poplar Chase Lane, Boise, Idaho."
}"""

# Input the key value that you want to search
keyVal = input("Enter a key value: \n")

# load the json data
customer = json.loads(customerData)
# Search the key value using 'in' operator
if keyVal in customer:
    # Print the success message and the value of the key
    print("%s is found in JSON data" %keyVal)
    print("The value of", keyVal,"is", customer[keyVal])
else:
    # Print the message if the value does not exist
    print("%s is not found in JSON data" %keyVal)