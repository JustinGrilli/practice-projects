class Employee:

    def __init__(self, *args):
        self.name = args[0]
        self.age = args[1]
        self.id = args[2]


emp1 = Employee('justin', 26, 123)

print emp1.age
