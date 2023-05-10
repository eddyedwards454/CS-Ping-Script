vendors = ['wayne','Jenny','Thomas','Harry']

for index, each in enumerate(vendors):
    print(str(index) + '  ' + each)

for index, each in enumerate(vendors):
    if each == 'Thomas':
        print('wayne index is :' + str(index))
