class Person:
    def __init__(self, name, old):
        self.__name = name
        self.__old = old

    def set_old(self, old):
        self.__old = old

    @property
    def get_old(self):
        return self.__old


p = Person("Сергей", 20)
p.get_old = 35
print(p.get_old)
