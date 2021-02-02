separator = ";"


class CSVWriter:

    def __init__(self, file_name: str, agents: []) -> None:
        self.file = open("logs/" + file_name + ".csv", "w")
        for agent in agents:
            self.file.write(str(agent.id_ag) + separator)
        self.file.write("max_crit" + "\n")

    def writeLine(self, agents: []) -> None:
        max_crit = 0.0
        for agent in agents:
            self.file.write(str(agent.criticality) + separator)
            if abs(agent.criticality) > max_crit:
                max_crit = abs(agent.criticality)
        self.file.write(str(max_crit) + "\n")

    def end(self):
        self.file.close()
