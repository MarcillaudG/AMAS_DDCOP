class Variables:
    def __init__(self, name: str, reliability: int, size: int):
        self.name = name
        self.reliability = reliability
        self.value = 0.0
        self.size = size

    def __lt__(self, other):
        return self.reliability < other.reliability

    def __repr__(self):
        return self.name + "[reliability: " + str(self.reliability) + " ,value: " +\
               str(self.value) + " ,size:"+str(self.size)
