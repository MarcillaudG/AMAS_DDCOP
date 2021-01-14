from agents.AgentStation import AgentStation
from world.Variables import Variables
from datetime import date


class DCOPWriter:

    def __init__(self, scenario: str, variables: [str]):
        self.agents = {}
        self.variables = variables
        self.scenario = scenario

    def addAgent(self, ag: AgentStation, cycle: int):
        id_ag = ag.id_ag
        if id_ag in self.agents.keys():
            raise AgentAlreadyExistError(id_ag)
        else:
            self.agents[id_ag] = {}
            self.agents[id_ag]["CycleBegin"] = cycle
            self.agents[id_ag]["Variables"] = {}
            for var in ag.decision_variable.keys():
                self.agents[id_ag]["Variables"][var] = ag.decision_variable[var]
            self.agents[id_ag]["Computing"] = ag.computing_capacity
            self.agents[id_ag]["Communication"] = ag.communication_capacity

    # Precise the end cycle
    def destroyAgent(self, id_ag: int, cycle: int):
        if id_ag not in self.agents.keys():
            raise AgentDoesntExistError(id_ag)
        else:
            if "CycleEnd" in self.agents[id_ag].keys():
                raise AgentDoesntExistError(id_ag)
            else:
                self.agents[id_ag]["CycleEnd"] = cycle

    # End the resolution
    def endResolution(self, cycle: int):
        for id_ag in self.agents.keys():
            if "CycleEnd" not in self.agents[id_ag].keys():
                self.agents[id_ag]["CycleEnd"] = cycle

    def writeDCOP(self):
        # file_name = self.scenario + "_" + str(date.today())
        file_name = "DCOP/" + self.scenario
        file = open(file_name, "w")
        # Head
        file.write("name:" + self.scenario + "\n")
        file.write("objective: max\n")

        # domain
        file.write("\ndomains:\nd:\ntype: d\nvalues: [0,1]\n\n")

        # variables
        file.write("variables:\n")
        for var in self.variables:
            file.write(var + ":\ndomain: d\n")

        # constraints
        # TODO

        file_event = open(file_name+"_events", "w")
        # agents
        file.write("agents: [")
        list_agents = ""
        for id_ag in self.agents.keys():
            # file.write("a"+str(id_ag) + ",")
            if list_agents != "":
                list_agents += ","
            list_agents += "a"+str(id_ag)
            cycle_begin = self.agents[id_ag]["CycleBegin"]
            file_event.write("AgentCreation:\na" + str(id_ag) + ": " + str(cycle_begin) + "\n")
            if "CycleEnd" in self.agents[id_ag].keys():
                cycle_end = self.agents[id_ag]["CycleEnd"]
                file_event.write("AgentDestruction:\na" + str(id_ag) + ": " + str(cycle_end) + "\n")
        file.write(list_agents)
        file.write("]")
        file.close()
        file_event.close()


class AgentAlreadyExistError:

    def __init__(self, id_ag: int):
        print("Agent: " + str(id_ag) + " already in agents")


class AgentDoesntExistError:
    def __init__(self, id_ag: int):
        print("Agent: " + str(id_ag) + " not in agents")


class AgentAlreadyDestroyError:
    def __init__(self, id_ag: int):
        print("Agent: " + str(id_ag) + " already destroy")
