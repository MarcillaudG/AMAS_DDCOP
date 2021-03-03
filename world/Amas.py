from time import sleep
import random
from agents.AgentStation import AgentStation
from agents.Messages import Message
from world.Environment import Environment
from world.Network import Network
from writers.CSVWriter import CSVWriter
from writers.DCOPWriter import DCOPWriter
from writers.LogCriticality import LogCriticality
from colorama import *

from writers.NetworkWriter import NetworkWriter


class Amas:
    def __init__(self, experiment="DEFAULT", init_ag=9, proba_destr_agent=0.01, appar_ag=0.01, nb_data=20,
                 computation_max=10, variation_comp=0.25, communication_max=10, variation_comm=0.25,
                 network_size=10000, max_cycle=20, neighbourhood=0):
        self.agents = []
        self.variables = {}
        self.experiment = experiment
        self.logCriticality = LogCriticality(experiment)
        self.all_var = {
            "init_ag": init_ag,
            "proba_destr_agent": proba_destr_agent,
            "appar_ag": appar_ag,
            "nb_data": nb_data,
            "computation_max": computation_max,
            "variation_comp": variation_comp,
            "communication_max": communication_max,
            "variation_comm": variation_comm,
            "network_size": network_size,
            "max_cycle": max_cycle,
            "neighbourhood": neighbourhood
        }
        self.mailbox = []
        self.all_id_ag = 0
        if self.experiment == "DEFAULT":
            self.__beginExperimentDefault__()
        else:
            self.__readScenario__(self.experiment)
            self.__beginExperiment__()

    # read the file and create the corresponding experiment
    def __readScenario__(self, experiment: str) -> None:
        file = open("scenarios/" + experiment, "r")
        for line in file.read().split("\n"):
            print(line)
            line_split = line.split("=")
            if "." in line_split[1]:
                self.all_var[line_split[0]] = float(line_split[1])
            else:
                self.all_var[line_split[0]] = int(line_split[1])
        print(str(self.all_var))

    # Return a list with all neighbors ofthe given agent
    def get_neighbors(self, id_ag: int) -> []:
        res = []
        for agent in self.agents:
            if agent.id_ag != id_ag:
                res.append(agent)
        return res

    # The experiment used for test and controllable
    # WARNING use only for debugging purposes
    # Use __beginExperiment__ instead
    def __beginExperimentDefault__(self) -> None:
        print("BEGIN of the test Experiment with parameters: " + str(self.all_var))
        self.environment = Environment(self.all_var["nb_data"])
        self.writer = DCOPWriter(self.experiment, self.environment.variables.keys())
        # Creation of 9 agents
        for i in range(0, self.all_var["init_ag"]):
            # No limit for communication
            agent = AgentStation(self.all_id_ag, computing_capacity=self.all_var["computation_max"],
                                 communication_capacity=self.all_var["communication_max"],
                                 environment=self.environment, network=self.network)
            '''self.agents.append(AgentStation(self.all_id_ag, computing_capacity=self.all_var["computation_max"],
                                            communication_capacity=self.all_var["communication_max"],
                                            environment=self.environment, network=self.network))'''
            self.agents.append(agent)
            # self.writer.addAgent(agent, 0)
            self.all_id_ag += 1

    # The method use to start the experiment
    def __beginExperiment__(self) -> None:
        self.distri_capa = [random.gauss(self.all_var["computation_max"],
                                         self.all_var["variation_comp"]) for i in range(1000)]
        self.network = Network(self.all_var["network_size"])
        self.environment = Environment(self.all_var["nb_data"])
        self.writer = DCOPWriter(self.experiment, self.environment.variables.keys())
        com_range = 999999
        if self.all_var["neighbourhood"] != 0:
            com_range = self.all_var["neighbourhood"]
        # Creation of agents
        for i in range(0, self.all_var["init_ag"]):
            # Specification of agent
            agent = AgentStation(self.all_id_ag,
                                 computing_capacity=int(self.distri_capa[self.all_id_ag % len(self.distri_capa)]),
                                 communication_capacity=self.all_var["communication_max"],
                                 environment=self.environment, network=self.network, com_range=com_range)
            '''self.agents.append(AgentStation(self.all_id_ag, computing_capacity=self.all_var["computation_max"],
                                            communication_capacity=self.all_var["communication_max"],
                                            environment=self.environment, network=self.network))'''
            self.agents.append(agent)
            self.writer.addAgent(agent, 0)
            self.environment.addAgentToGrid(self.all_id_ag)
            self.all_id_ag += 1
        self.writerCSV = CSVWriter(self.experiment, self.agents)
        self.writerNetwork = NetworkWriter(self.experiment)

    # First implementation, messages are sent to all
    def send_messages(self, to_send: [Message]) -> None:
        self.mailbox = self.mailbox + to_send
        pass

    ####################################################################################################################
    # System Cycle
    ####################################################################################################################

    def __beginCycle__(self) -> None:
        self.network.__cycleBegin__()

    def __agentsCycle__(self) -> None:
        for agent in self.agents:
            # neighbours = self.environment.getNeighbours(agent.id_ag, agent.com_range)
            neighbours = []
            for other in self.agents:
                if other.id_ag != agent.id_ag:
                    neighbours.append(other.id_ag)
            agent.perceive(neighbours)
            agent.decide()
            agent.act()

    def __endCycle__(self) -> None:
        total = 0
        ag_to_remove = []
        self.network.__cycleEnd__()
        for agent in self.agents:
            agent.receive_message_from_netowrk()
            agent.computeCriticality()
            total += agent.computeEfficiencyLimit()
        self.__drawAgent__()
        # for agent in self.agents:
        # tirage = random.random()
        # if tirage < self.all_var["proba_destr_agent"]:
        #    ag_to_remove.append(agent)
        tirage = random.random()
        if tirage < self.all_var["proba_destr_agent"]:
            ind_ag = random.randint(0, len(self.agents) - 1)
            ag_to_remove.append(self.agents[ind_ag])
        print("Total for the cycle : " + str(total))
        print("NBMESSAGES : " + str(self.network.nb_messages()))
        cpt = 0
        self.logCriticality.writeCriticality(self.cycle, self.agents)
        self.writerCSV.writeLine(self.agents, total)
        self.writerNetwork.writeCycle(self.cycle, self.network)
        for agent_to_r in ag_to_remove:
            self.agents.remove(agent_to_r)
            # self.writer.destroyAgent(agent_to_r.id_ag, self.cycle)
            del agent_to_r
            cpt += 1
        if cpt > 0:
            print("DESTRUCTION -> " + str(ag_to_remove))

        com_range = 999999
        if self.all_var["neighbourhood"] != 0:
            com_range = self.all_var["neighbourhood"]
        while cpt > 0:
            agent = AgentStation(self.all_id_ag, computing_capacity=self.all_var["computation_max"],
                                 communication_capacity=self.all_var["communication_max"],
                                 environment=self.environment, network=self.network, com_range=com_range)
            '''self.agents.append(AgentStation(self.all_id_ag, computing_capacity=self.all_var["computation_max"],
                                            communication_capacity=self.all_var["communication_max"],
                                            environment=self.environment, network=self.network))'''
            self.agents.append(agent)
            self.writer.addAgent(agent, self.cycle)
            self.all_id_ag += 1
            cpt -= 1

    def __run__(self, max_cycle: int, mode="auto", time=1) -> None:
        if mode == "auto":
            for i in range(0, max_cycle):
                self.cycle = i
                print("Begin cyle " + str(i))
                self.__beginCycle__()
                self.__agentsCycle__()
                self.__endCycle__()
                print("END cyle " + str(i))
                # sleep(time)
        if mode == "manuel":
            i = 0
            stop = False
            while i < max_cycle and stop == 1:
                self.__beginCycle__()
                self.__agentsCycle__()
                self.__endCycle__()
                i = i + 1
                stop = input("Continue ? 0 stop / 1 continue")
        print("RUN ENDED WITHOUT ERROR")
        self.writer.writeDCOP(self.environment)
        self.logCriticality.endLog()
        self.writerCSV.end()
        self.writerNetwork.end()

    def __drawAgent__(self) -> None:
        i = 0
        nb_col = int(len(self.agents) / 3)
        while i + nb_col - 1 < len(self.agents):
            j = 0
            str_to_write = ""
            while j < int(nb_col):
                str_to_write += "O____O "
                j += 1
            str_to_write += "\n"
            j = 0
            while j < int(nb_col):
                str_to_write += "|" + self.agents[i + j].strID() + "|\\ "
                j += 1
            str_to_write += "\n"
            j = 0
            while j < int(nb_col):
                str_to_write += "|" + self.agents[i + j].strCrit() + "|/ "
                j += 1
            str_to_write += "\n"
            j = 0
            while j < int(nb_col):
                str_to_write += "O¯¯¯¯O "
                j += 1
            print(Fore.RED + str_to_write)
            print(Style.RESET_ALL)
            i += nb_col
