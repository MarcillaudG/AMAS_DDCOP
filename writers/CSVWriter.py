separator = ";"


class CSVWriter:

    def __init__(self, file_name: str, agents: []) -> None:
        self.file = open("logs/" + file_name + ".csv", "w")
        for agent in agents:
            self.file.write(str(agent.id_ag) + separator)
        self.file.write("max_crit" + separator)
        self.file.write("moyenne" + separator)
        self.file.write("creation" + separator)
        self.file.write("destruction" + "\n")
        self.last_agents = []
        self.last_agents.extend(agents)

    def writeLine(self, agents: []) -> None:
        max_crit = 0.0
        moyenne = 0.0
        new = []
        destr = []
        for agent in agents:
            self.file.write(str(agent.criticality) + separator)
            if abs(agent.criticality) > max_crit:
                max_crit = abs(agent.criticality)
            moyenne += abs(agent.criticality)
            if agent not in self.last_agents:
                new.append(agent)
        for agent in self.last_agents:
            if agent not in agents:
                destr.append(agent)
        self.file.write(str(max_crit) + separator)
        moyenne = moyenne / len(agents)
        self.file.write(str(moyenne) + separator)

        for ag in new:
            self.file.write(str(ag.id_ag) + "|")
        self.file.write(separator)
        for ag in destr:
            self.file.write(str(ag.id_ag) + "|")
        self.file.write("\n")
        self.last_agents.clear()
        self.last_agents.extend(agents)

    def end(self):
        self.file.close()
