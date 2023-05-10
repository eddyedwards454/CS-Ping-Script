
def Test(x,secound):
    z = x + secound
    print(z)

Test(10,100)


#Calling via position or name below
Test(10, secound=450)

# def Test2(x,y,z):
#     print(y)
#     print(x)
#     print(z)
#
#
# Test2(10,20,30)
# for w in Test2(100,200,300):
#     print(w)

def hello(x):
    print(x)

hello('wayne')

def hello1(x):
    print('Hello World my name is :' + x)

hello1('Wayne Edwards')

def hello2(name):
    print('Hello {}'.format(name))

hello2('Wayne Edwards 2')

def print_square(num):
    square = num**2
    square2 = square + square
    print('The square of {} is {} and times that again {}.'.format(num,square,square2))

print_square(6)

def draw_rect(rows, clos, char):
    for row in range(rows):
        for col in range(clos):
            # print(char, end='   ')
            print(char)
        print()
draw_rect(3, 8, '*')