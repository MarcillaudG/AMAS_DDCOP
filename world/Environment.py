import random
import numpy as np

from world.Variables import Variables

MAX_ROW = 10
MAX_COL = 10


class Environment:

    def __init__(self, nb_var: int):
        # Creation of nb_var variables
        self.variables = {}
        self.distribution_gauss_sensed = {}
        for i in range(0, nb_var):
            self.variables["var" + str(i)] = Variables("var" + str(i), 0, 1)
            self.distribution_gauss_sensed["var" + str(i)] = [random.gauss(5, 1.5) for i in range(1000)]
        self.nb_agents_in_grid = 0
        self.grid = np.array([[None] * MAX_COL] * MAX_ROW)
        self.agents = {}

    def getReliability(self, name: str, id_com: int):
        return self.distribution_gauss_sensed[name][id_com % len(self.distribution_gauss_sensed[name])]

    # ADD the given agent next to a random one
    def addAgentToGrid(self, id_ag: int) -> bool:
        if self.nb_agents_in_grid == 0:
            self.grid[int(MAX_ROW / 2)][int(MAX_COL / 2)] = id_ag
            self.agents[id_ag] = (int(MAX_ROW / 2), int(MAX_COL / 2))
            self.nb_agents_in_grid += 1
        else:
            first_neighb = list(self.agents.keys())[random.randint(0, self.nb_agents_in_grid-1)]
            dist = 1
            found = False
            x_neighb, y_neighb = self.agents[first_neighb]
            possible_cases = []
            while not found and (
                    x_neighb - dist >= 0 or dist + x_neighb < MAX_ROW or y_neighb - dist >= 0 or dist + y_neighb < MAX_COL):
                j = max(x_neighb - dist, 0)
                while j <= x_neighb + dist and j < MAX_ROW:
                    k = max(y_neighb - dist, 0)
                    while k <= y_neighb + dist and k < MAX_COL:
                        if self.grid[j][k] is None and (j, k) not in possible_cases:
                            possible_cases.append((j, k))
                            found = True
                        k += 1
                    j += 1
                dist += 1
            if found:
                new_x, new_y = possible_cases[random.randint(0, len(possible_cases)-1)]
                self.grid[new_x][new_y] = id_ag
                self.agents[id_ag] = (new_x, new_y)
                self.nb_agents_in_grid += 1
                return True
            else:
                return False

    # Add an agent to the grid with its coordinates
    def addAgentToGridWithCoord(self, id_ag: int, x: int, y: int):
        if 0 <= x < MAX_ROW and 0 <= y < MAX_COL:
            if self.grid[x][y] is None:
                self.grid[x][y] = id_ag
                self.agents[id_ag] = (x, y)
                self.nb_agents_in_grid += 1
            else:
                print("ALREADY AN AGENT ERROR")
        else:
            print("WRONG COORDINATES ERROR")

    # Remove an agent from the nevironment
    def removeAgentFromGrid(self, id_ag: int) -> None:
        x, y = self.agents[id_ag]
        self.grid[x][y] = None
        self.agents.pop(id_ag)

    # Return a list of all neigbhours of an agent
    def getNeighbours(self, id_ag: int, dist: int) -> []:
        res = []
        x, y = self.agents[id_ag]
        j = max(x - dist, 0)
        while j <= x + dist and j < MAX_ROW:
            k = max(y - dist, 0)
            while k <= y + dist and k < MAX_COL:
                if self.grid[j][k] is not None and self.grid[j][k] not in res and (j, k) != (x, y):
                    res.append(self.grid[j][k])
                k += 1
            j += 1
        return res

    def drawGrid(self) -> None:
        strgrid = ""
        for i in range(MAX_ROW):
            for j in range(MAX_COL):
                if self.grid[i][j] is not None:
                    strgrid +=  str(self.grid[i][j]) + "|"
                else:
                    strgrid += " |"
            strgrid += "\n"
        print(strgrid)

    def getPosition(self, id_ag):
        return self.agents[id_ag]

    def replaceAgent(self, new_id, x, y):
        self.agents.pop(self.grid[x][y])
        self.agents[new_id] = (x, y)
        self.grid[x][y] = new_id