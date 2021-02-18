from world.Network import Network

separator = ";"


class NetworkWriter:
    def __init__(self, scenario: str):
        self.file = open("logs/" + scenario + "_network.csv", "w")

    def writeCycle(self, cycle: int, network: Network) -> None:
        self.file.write(str(cycle) + ";")
        for mess in network.releaseMessages():
            self.file.write(mess.name + "_" + str(mess.sender) + separator)
        self.file.write("\n")

    def end(self):
        self.file.close()
