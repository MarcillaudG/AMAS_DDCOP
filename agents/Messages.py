class Message:
    def __init__(self, var: str, id_ag: int, weight: int, value: float):
        self.name = var
        self.sender = id_ag
        self.weight = weight
        self.value = value

    def __repr__(self):
        return self.name + " ID: " + str(self.sender) + " : " + str(self.weight) + " : " + str(self.value)


class MessageCrit:
    def __init__(self, id_ag:int, crit: float):
        self.sender = id_ag
        self.crit = crit
        self.weight = 1

    def __repr__(self):
        return "MESSAGECRIT: SENDER => " + str(self.sender) + " CRIT => " + str(self.crit)
