#This is a function
#Built-in functions ( As the name suggests, these functions come with the Python language, for example, help() to ask for any help, max()- to get maximum value, type()- to return the type of an object and many more.)
# User-defined functions ( These are the functions that users create to help them, like the “sum” function we have created below).
# Anonymous Functions (also called lambda functions and unlike normal function which is defined using def keyword are defined using lambda keyword)
def sum(num1, num2):
   return (num1 + num2)

print(sum(5,6))

# A method in python is somewhat similar to a function, except it is associated with object/classes. Methods in python are very similar to functions except for two major differences.
# The method is implicitly used for an object for which it is called.
# The method is accessible to data that is contained within the class.

class Pet(object):
   def my_method(self):
      print("I am a Cat")

   def anothe_metod(self):
      print("I am a dog")

# Assignes cat varibale to the class __main__.Pet
cat = Pet()
print(type(cat))
# Assignes dog varibale to the class __main__.Pet
dog = Pet()
print(type(dog))
#Calls the method "anothe_metod" from class to which the dog varibale was assigne in the fast place
dog.anothe_metod()
#Calls the method "mymethod" from class to which the cat varibale was assigne in the fast place

cat.my_method()