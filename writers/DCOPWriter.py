from agents.AgentStation import AgentStation
from world.Environment import Environment
from world.Variables import Variables
from datetime import date


class DCOPWriter:

    def __init__(self, scenario: str, variables: []):
        self.agents = {}
        self.variables = variables
        self.scenario = scenario
        self.dict_env_var_to_ag_var = {}
        for var in variables:
            self.dict_env_var_to_ag_var[var] = {}

    def addAgent(self, ag: AgentStation, cycle: int):
        id_ag = ag.id_ag
        if id_ag in self.agents.keys():
            raise AgentAlreadyExistError(id_ag)
        else:
            self.agents[id_ag] = {}
            self.agents[id_ag]["CycleBegin"] = cycle
            self.agents[id_ag]["Variables"] = []
            for var in ag.decision_variable.keys():
                self.agents[id_ag]["Variables"].append(str(ag.decision_variable[var]) + "_" + str(id_ag))
                var_name = str(ag.decision_variable[var]) + "_" + str(id_ag)
                self.dict_env_var_to_ag_var[var][var_name] = {}
            self.agents[id_ag]["Computing"] = ag.getComputingCapacity()
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

    def writeDCOP(self, env: Environment):
        space = "    "
        nb_space = 1
        # file_name = self.scenario + "_" + str(date.today())
        file_name = "DCOP/" + self.scenario
        file = open(file_name + ".yaml", "w")
        # Head
        file.write("name: " + self.scenario + "\n")
        file.write("objective: max\n")

        # domain
        file.write("\ndomains:\n" + space + "d: \n" + space + space + "values: [0, 1]\n\n")

        ##################################################################################################
        # variables
        ##################################################################################################
        all_var = []
        all_var_ag = {}
        for id_ag in self.agents.keys():
            all_var_ag[id_ag] = []
        file.write("variables:\n")
        for id_ag in self.agents.keys():
            for other_ag in self.agents.keys():
                if other_ag != id_ag:
                    all_var_ag[other_ag] += self.agents[id_ag]["Variables"]
            all_var += self.agents[id_ag]["Variables"]
            for var in self.agents[id_ag]["Variables"]:
                file.write(space + var + ":\n" + space + space + "domain: d\n" + space + space + "initial_value: 0\n\n")

        '''line_cong = "a= " + str(all_var[0])
        for i in range(1, len(all_var)):
            var = all_var[i]
            line_cong += " + " + str(var)'''

        ##################################################################################################
        # constraints
        ##################################################################################################
        file.write("constraints:\n")
        for id_ag in self.agents.keys():
            line_cong = "a= " + str(all_var_ag[id_ag][0])
            for i in range(1, len(all_var_ag[id_ag])):
                var = all_var_ag[id_ag][i]
                line_cong += " + " + str(var)
            # charge computation
            file.write(space + "congestion_comput_ag" + str(id_ag) + ":\n" + space + space + "type: intention\n")
            # function
            file.write(space + space + "function: |\n" + space + space + space + line_cong)
            # TODO Function
            file.write("\n" + space + space + space +
                       "return - max(a - " + str(self.agents[id_ag]["Computing"]) + ", 0)\n\n")

            # Rempli chaque variable
            for var in self.dict_env_var_to_ag_var.keys():
                for var_name in self.dict_env_var_to_ag_var[var]:
                    # var_name = var + "_" + str(id_ag)
                    # self.dict_env_var_to_ag_var[var][var_name] = {}
                    for other_ag in self.agents.keys():
                        other_ag_var_name = var + "_" + str(other_ag)
                        if other_ag_var_name in self.agents[other_ag]["Variables"]:
                            if other_ag != id_ag:
                                value_sensed = env.distribution_gauss_sensed[var][other_ag]
                                self.dict_env_var_to_ag_var[var][var_name][other_ag_var_name] = value_sensed
                            else:
                                value_sensed = env.distribution_gauss_sensed[var][other_ag]
                                self.dict_env_var_to_ag_var[var][var_name][other_ag_var_name] = value_sensed

        for var in self.dict_env_var_to_ag_var.keys():
            for ag_var in self.dict_env_var_to_ag_var[var].keys():
                file.write(space + "C_utility_ag_" + str(ag_var))
                file.write(":\n" + space + space + "type: intention\n" + space + space + "function: max([")
                all_var_used = []
                first = True
                for other_ag_var_name in self.dict_env_var_to_ag_var[var][ag_var]:
                    if not first:
                        file.write(", ")
                    else:
                        first = False
                    file.write(other_ag_var_name + " * ")
                    file.write(str(self.dict_env_var_to_ag_var[var][ag_var][other_ag_var_name]))
                    all_var_used.append(other_ag_var_name)

                file.write("])\n\n")
                # file.write(space + space + "variables: " + str(all_var_used) + "\n\n")
        file_event = open(file_name + "_events.yaml", "w")
        # agents
        file.write("agents: [")
        list_agents = ""
        for id_ag in self.agents.keys():
            # file.write("a"+str(id_ag) + ",")
            if list_agents != "":
                list_agents += ","
            list_agents += "a" + str(id_ag)
            cycle_begin = self.agents[id_ag]["CycleBegin"]
            file_event.write("AgentCreation:\na" + str(id_ag) + ": " + str(cycle_begin) + "\n")
            if "CycleEnd" in self.agents[id_ag].keys():
                cycle_end = self.agents[id_ag]["CycleEnd"]
                file_event.write("AgentDestruction:\na" + str(id_ag) + ": " + str(cycle_end) + "\n")
        file.write(list_agents)
        file.write("]\n\n")

        ##################################################################################################
        # HOSTING COSTs
        ##################################################################################################
        '''file.write("hosting_costs:\n" + space + "default: -10000\n")
        for id_ag in self.agents.keys():
            file.write(space + "a" + str(id_ag) + ":\n" + space + "computations:\n")
            for var in self.agents[id_ag]["Variables"]:
                file.write(space + space + "C_utility_ag_" + str(var) + ": 0" + "\n")
            for var in self.agents[id_ag]["Variables"]:
                file.write(space + space + str(var) + ": 0" + "\n")
        file.close()
        file_event.close()'''

        file_distri = open("DCOP/distri_" + self.scenario + ".yaml", "w")
        file_distri.write("distribution:\n")
        for id_ag in self.agents.keys():
            file_distri.write(space + "a" + str(id_ag) + ": [")
            first = True
            for var in self.agents[id_ag]["Variables"]:
                if not first:
                    file_distri.write(", ")
                else:
                    first = False
                file_distri.write(var)
            file_distri.write("]\n")
        file_distri.close()


class AgentAlreadyExistError:

    def __init__(self, id_ag: int):
        print("Agent: " + str(id_ag) + " already in agents")


class AgentDoesntExistError:
    def __init__(self, id_ag: int):
        print("Agent: " + str(id_ag) + " not in agents")


class AgentAlreadyDestroyError:
    def __init__(self, id_ag: int):
        print("Agent: " + str(id_ag) + " already destroy")
