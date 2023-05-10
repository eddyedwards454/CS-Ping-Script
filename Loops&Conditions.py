vendors = ['wayne','Jenny','Thomas','Harry']

best_people = ['wayne','Jenny','Thomas']

for vendor in vendors:
    if vendor not in best_people:
        print('Ones that are not in secound list   ' + vendor)
    # else:
    #     print(test)

sprintTimes = {
    'Sarah': 22.20,
    'James': 21.05,
    'Michelle': 21.97,
    'Zoey': 22.12,
    'Steve': 21.21,
}

# Check if we have Steve's data
if 'Steve' in sprintTimes:
    print("Steve's sprint time is:", sprintTimes['Steve'])
else:
    print("We don't have Steve's sprint time.")

sprintTimes = {
    'Sarah': 22.20,
    'James': 21.05,
    'Michelle': 21.97,
    'Zoey': 22.12,
    'Steve': 21.21,

}

# Check if we have Steve's data
if 'Steve' in sprintTimes:
    print("Steve's sprint time is :", sprintTimes['Steve'])
    # continue
else:
    for key,value in sprintTimes.items():
        print(key + ':' + str(value))
    # print("We don't have Steve's sprint time.")

number = 0

for number in range(10):
   number = number + 1

   if number == 5:
        pass# break here

   print('Number is ' + str(number))

print('Out of loop')

counter = 10
while counter < 0 :
    print(counter)
    counter = counter - 1
print('Take off now ')

for index, each in enumerate(vendors):
    print(index + ' ' + each)

