from random import gauss

from world.Variables import Variables


class Environment:

    def __init__(self, nb_var: int) -> object:
        # Creation of nb_var variables
        self.variables = {}
        self.distribution_gauss_sensed = {}
        for i in range(0, 20):
            self.variables["var"+str(i)] = Variables("var"+str(i), 0, 1)
            self.distribution_gauss_sensed["var"+str(i)] = [gauss(5, 1.5) for i in range(100)]

    def getReliability(self, name: str, id_com: int):
        return self.distribution_gauss_sensed[name][id_com % len(self.distribution_gauss_sensed[name])]
