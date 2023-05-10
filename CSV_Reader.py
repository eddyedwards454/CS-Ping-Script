import csv
with open('wayne.csv', 'r') as f:
    reader = csv.reader(f)
    dict_test =dict()


    # command below removes first line in CSV
    next(reader)
    for row in reader:
        dict_test[row[0]] = row[3]
    print(dict_test)

    max_test = max(dict_test.values())
    print(max_test)

    for k , v in dict_test.items():
        if max_test == v:
            print(f'test:{k}, name:{v}')






        # print(dict_test)
