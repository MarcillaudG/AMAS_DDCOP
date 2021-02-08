class LogCriticality:

    def __init__(self, scenario: str):
        self.file = open("logs/" + scenario, "w")
        self.last_comp = {}

    def writeCriticality(self, cycle: int, agents: []) -> None:
        self.file.write("#################################################\n")
        self.file.write("Cycle: " + str(cycle) + "\n")
        self.file.write("#################################################\n")
        max_crit = 0.0
        worst_agent = -1
        for agent in agents:
            if agent.id_ag not in self.last_comp.keys():
                self.last_comp[agent.id_ag] = agent.communication_capacity
            self.file.write(str(agent))
            if self.last_comp[agent.id_ag] != agent.communication_capacity:
                self.file.write(" Modif : " + str(agent.communication_capacity - self.last_comp[agent.id_ag]))
            self.file.write("\n")
            self.last_comp[agent.id_ag] = agent.communication_capacity
            if abs(agent.criticality) > abs(max_crit):
                max_crit = agent.criticality
                worst_agent = agent.id_ag
        self.file.write("WORST AGENT: " + str(worst_agent) + " With " + str(max_crit) + "\n")

    def endLog(self):
        self.file.close()
