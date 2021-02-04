class LogCriticality:

    def __init__(self, scenario: str):
        self.file = open("logs/" + scenario, "w")

    def writeCriticality(self, cycle: int, agents: []) -> None:
        self.file.write("#################################################\n")
        self.file.write("Cycle: " + str(cycle) + "\n")
        self.file.write("#################################################\n")
        max_crit = 0.0
        worst_agent = -1
        for agent in agents:
            self.file.write(str(agent) + "\n")
            if abs(agent.criticality) > abs(max_crit):
                max_crit = agent.criticality
                worst_agent = agent.id_ag
        self.file.write("WORST AGENT: " + str(worst_agent) + " With " + str(max_crit) + "\n")

    def endLog(self):
        self.file.close()
