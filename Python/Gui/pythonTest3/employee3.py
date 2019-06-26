class employee4:
    'Common base class for all employees'
   empCount = 0

   def __init__(self, name, salary):
      self.name = name
      self.salary = salary
      employee4.empCount += 1
      print "Inside constructor (file Employee2)"
   
   def displayCount(self):
     print "Total Employee %d" % employee4.empCount

   def displayEmployee(self):
      print "Name : ", self.name,  ", Salary: ", self.salary