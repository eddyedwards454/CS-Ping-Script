
x = input("What is the X value")
y = input('What is the Y value')

z = int(x)
w = int(y)

def add(z, w):
    return z + w
d = (add(z=45,w=45))
print(d)

def add1(*args):
    print(args)


add2(a=10, b=20, c=30, d=40)

def add2(**kwargs):
    print(kwargs)
    return (kwargs.values())




