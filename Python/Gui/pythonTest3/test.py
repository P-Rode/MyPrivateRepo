from Employee import *
from Employee2 import *
#from employee3 import *


# Function definition is here
def printme( st ):
    "This prints a passed string into this function"
    print st;
    return;
# Now you can call printme function
printme("I'm first call to user defined function!")
printme("Again second call to the same function")
print "-------------------------------"


"This would create first object of Employee class"
emp1 = Employee("Zara", 2000)
"This would create second object of Employee class"
emp2 = Employee("Manni", 5000)

"This would create first object of Employee class"
emp3 = Employee2("Per", 1968)
"This would create second object of Employee class"
emp4 = Employee2("Elsabeth Rodenvall", 1969)

"This would create first object of Employee class"
#emp5 = employee4("Filip", 1998)
"This would create second object of Employee class"
#emp6 = employee4("Jona", 1999)

emp1.displayCount()
emp2.displayEmployee()
emp3.displayCount()
emp4.displayEmployee()