from time import sleep

from agents.Messages import Message, MessageCrit

from world.Environment import Environment
from world.Network import Network
from world.Variables import Variables


class AgentStation:

    id_ag = None

    def __init__(self, id_ag: int, computing_capacity: int, communication_capacity: int,
                 environment: Environment, network: Network):

        self.id_ag = id_ag
        self.environment = environment
        self.network = network
        self.var = {}
        self.neighborhood = []
        self.decision_variable = {}
        self.sensors_variable = []
        self.computing_capacity = computing_capacity
        self.communication_capacity = communication_capacity
        self.useless_variable = []
        self.to_send = []
        self.weight_before = 0
        self.sent = []
        self.received_messages = []
        self.__initUtility__()

    def __initUtility__(self):
        for env_var in self.environment.variables.keys():
            utility = self.environment.getReliability(env_var, self.id_ag)
            if utility >= 2:
                self.decision_variable[env_var] = Variables(env_var, utility, self.environment.variables[env_var].size)

    def perceive(self, neighbors: []):
        print("PERCEIVE PHASE " + str(self.id_ag))
        # perceive my neighbours
        self.neighborhood = neighbors

        # what my sensors gather
        # not used for now
        # self.sensors_variable = sensed
        self.sent.extend(self.to_send)
        # perceive the variable sorted by reliability
        self.decision_variable = dict(sorted(self.decision_variable.items(), key=lambda item: item[1], reverse=True))

    def decide(self):
        print("DECIDE PHASE " + str(self.id_ag))
        # compute the best variable to send (to put at 1)
        # if an information less reliable than mine si shared, i share it
        # contrary, i do not
        less_reliable = []
        best_messages = {}

        # Manage criticality
        sum_weight = 0
        self.to_send.clear()
        for mess in self.received_messages:
            sum_weight += mess.weight
        criticality = max(0, sum_weight - self.computing_capacity)

        if criticality > 0:
            self.to_send.append(MessageCrit(id_ag=self.id_ag, crit=criticality))
            print(str(self) + " -> too many messages received " + str(sum_weight) + " instead of " +
                  str(self.computing_capacity))
        worst_crit = 0
        for mess in self.received_messages:
            if isinstance(mess, MessageCrit):
                worst_crit = max(mess.crit, worst_crit)
                self.received_messages.remove(mess)
            else:
                if mess.name in self.decision_variable.keys() and mess.sender in self.neighborhood:
                    var_tmp = self.analyse_message(mess)
                    if var_tmp.reliability > self.decision_variable[mess.name].reliability:
                        if mess.name not in best_messages.keys():
                            best_messages[mess.name] = mess
                        else:
                            var_best = self.analyse_message(best_messages[mess.name])
                            if var_best.reliability < var_tmp.reliability:
                                best_messages[mess.name] = mess
                        if mess.name not in less_reliable:
                            less_reliable.append(mess.name)
        # when an information is no longer shared  because of an agent missing and i can share it, i share it
        # first we delete all the items
        self.received_messages.clear()
        # when i know nothing, I send the ones I know useful for me
        print("SIZE : "+str(len(self.decision_variable.keys())))
        cumul_weight = 0
        weight_to_remove = worst_crit / len(self.neighborhood) + 1
        # pour toutes les variables
        for var in self.decision_variable.keys():
            # si je suis encore capable d'en envoyer
            if var not in less_reliable and len(self.to_send) < self.communication_capacity:
                # si je dois reduire un peu mon envoi ou non
                if worst_crit == 0 \
                        or cumul_weight+self.decision_variable[var].size < self.weight_before - weight_to_remove:
                    self.to_send.append(Message(var, self.id_ag, self.decision_variable[var].size, 0.0))
                    cumul_weight += self.decision_variable[var].size
        self.weight_before = cumul_weight

    def act(self):
        print("ACT PHASE " + str(self.id_ag))
        # send messages
        messages = []
        # print("TOSEND : -> " + str(self.to_send))
        # for var in self.to_send:
        #    messages.append(Message(var, self.id_ag, self.decision_variable[var].size, 0.0))
        self.network.sendMessages(self.to_send)

    def receive_messages(self, sent: [Message]):
        self.received_messages = sent

    def receive_message_from_netowrk(self):
        for mess in self.network.releaseMessages():
            self.received_messages.append(mess)

    # return the variable sent with the value analysed
    def analyse_message(self, mess: Message):
        id_other = mess.sender
        id_com = self.id_ag + id_other
        return Variables(mess.name, self.environment.getReliability(mess.name, id_other), mess.weight)

    # Compute the overall efficiency
    # The agent take the best variable among the available ones
    def computeEfficiency(self) -> int:
        efficiency = 0
        copy_received = []
        for mess in self.received_messages:
            copy_received.append(mess)
        for var in self.decision_variable.keys():
            related_mess = []
            reliab_var = self.decision_variable[var].reliability
            for mess in copy_received:
                if mess.name == var:
                    related_mess.append(mess)
                if self.environment.distribution_gauss_sensed[var][mess.sender] > reliab_var:
                    reliab_var = self.environment.distribution_gauss_sensed[var][mess.sender]
            efficiency += reliab_var
            for tor in related_mess:
                copy_received.remove(tor)

        return int(efficiency)

    # Compute the overall efficiency
    # The agent take the best variable among the available ones
    def computeEfficiencyLimit(self) -> int:
        efficiency = 0
        sum_weight = 0
        var_used = {}

        # copy the decision variable
        for env_var in self.decision_variable.keys():
            var_used[env_var] = self.decision_variable[env_var].reliability

        # select the best messages in the receive order
        # if it cannot compute more, it doest treat anymore
        for mess in self.received_messages:
            if not isinstance(mess, MessageCrit):
                if sum_weight <= self.computing_capacity and mess.name in var_used.keys():
                    if var_used[mess.name] < self.environment.distribution_gauss_sensed[mess.name][mess.sender]:
                        var_used[mess.name] = self.environment.distribution_gauss_sensed[mess.name][mess.sender]
                        sum_weight += mess.weight
        # compute the efficiency
        for var_name in var_used.keys():
            efficiency += var_used[var_name]

        return int(efficiency)

    def __str__(self):
        return "Agent "+str(self.id_ag)

    def __repr__(self):
        return "Agent "+str(self.id_ag)