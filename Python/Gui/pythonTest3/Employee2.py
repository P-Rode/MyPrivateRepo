class Employee2:
   'Common base class for all employees'
   empCount = 0

   def __init__(self, name, salary):
      self.name = name
      self.salary = salary
      Employee2.empCount += 1
      print "Inside constructor (file Employee2)"
   
   def displayCount(self):
     print "Total Employee %d" % Employee2.empCount

   def displayEmployee(self):
      print "Name : ", self.name,  ", Salary: ", self.salary