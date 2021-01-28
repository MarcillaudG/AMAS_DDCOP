import math
from time import sleep

from agents.Messages import Message, MessageCrit

from world.Environment import Environment
from world.Network import Network
from world.Variables import Variables

# TOO MUCH RECEIVED CRIT
THRESHOLD_TOO_MUCH_RECEIVED_MIN = 0.0
THRESHOLD_TOO_MUCH_RECEIVED_MAX = 0.50
MAX_TMR = 80.0
MIN_TMR = 0.0
COEFF_A_TMR = (MAX_TMR - MIN_TMR) / ((THRESHOLD_TOO_MUCH_RECEIVED_MAX - THRESHOLD_TOO_MUCH_RECEIVED_MIN) * 100)
COEFF_B_TMR = MAX_TMR - COEFF_A_TMR * (THRESHOLD_TOO_MUCH_RECEIVED_MAX * 100)

# TOO MUCH USELESS CRITICALITY
THRESHOLD_TOO_MUCH_USELESS_MIN = 0.05
THRESHOLD_TOO_MUCH_USELESS_MAX = 0.30
MAX_TMU = 80.0
MIN_TMU = 0.0
COEFF_A_TMU = (MAX_TMU - MIN_TMU) / ((THRESHOLD_TOO_MUCH_USELESS_MAX - THRESHOLD_TOO_MUCH_USELESS_MIN) * 100)
COEFF_B_TMU = MAX_TMU - COEFF_A_TMU * (THRESHOLD_TOO_MUCH_USELESS_MAX * 100)

# NOT ENOUGH CRITICALITY
THRESHOLD_NOT_ENOUGH_USELESS_MIN = 0.15
THRESHOLD_NOT_ENOUGH_USELESS_MAX = 0.0
MAX_NE = 100.0
MIN_NE = 0.0
COEFF_A_NE = (MAX_NE - MIN_NE) / ((THRESHOLD_NOT_ENOUGH_USELESS_MAX - THRESHOLD_NOT_ENOUGH_USELESS_MIN) * 100)
COEFF_B_NE = MAX_NE - COEFF_A_NE * (THRESHOLD_NOT_ENOUGH_USELESS_MAX * 100)

# SCORE DISTANCE CRIT
THRESHOLD_SCORE_MIN = 0.0
THRESHOLD_SCORE_MAX = 1.0
MAX_TS = 100.0
MIN_TS = 0.0
COEFF_A_TS = (MAX_TS - MIN_TS) / ((THRESHOLD_SCORE_MAX - THRESHOLD_SCORE_MIN) * 100)
COEFF_B_TS = MAX_TS - COEFF_A_TS * (THRESHOLD_SCORE_MAX * 100)

# IN CASE OF LOG
LOG_BASE = 2
POW_BASE = 2


class AgentStation:
    id_ag = None

    def __init__(self, id_ag: int, computing_capacity: int, communication_capacity: int,
                 environment: Environment, network: Network):

        self.id_ag = id_ag
        self.criticality = 0.0
        self.crits = {1: 0.0, 2: 0.0, 3: 0.0}
        self.environment = environment
        self.network = network
        self.var = {}
        self.neighborhood = {}
        self.decision_variable = {}
        self.sensors_variable = []
        self.computing_capacity = computing_capacity
        self.communication_capacity = communication_capacity
        self.useless_variable = []
        self.to_send = []
        self.weight_before = 0
        self.sent = []
        self.received_messages = []
        self.received_crit = []
        self.last_score = 0
        self.scores = {"min": 0, "max": 0}
        self.__initUtility__()

    def __initUtility__(self):
        for env_var in self.environment.variables.keys():
            utility = self.environment.getReliability(env_var, self.id_ag)
            if utility >= 2:
                self.decision_variable[env_var] = Variables(env_var, utility, self.environment.variables[env_var].size)
        score = self.computeEfficiencyLimit()
        self.scores["min"] = score
        self.scores["max"] = score
        self.last_score = score

    def perceive(self, neighbors: []):
        print("PERCEIVE PHASE " + str(self.id_ag))

        # perceive my neighbours
        new_dict = {}
        for new_neighbour in neighbors:
            new_dict[new_neighbour] = 0.0
            if new_neighbour in self.neighborhood.keys():
                new_dict[new_neighbour] = self.neighborhood[new_neighbour]
        self.neighborhood = new_dict
        print(str(self.neighborhood))
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
        # best_messages = {}

        # Manage criticality
        sum_weight = 0
        self.to_send.clear()
        for mess in self.received_messages:
            if mess.sender != self.id_ag:
                sum_weight += mess.weight

        # CCRIT
        # CRIT 2 -> TROP DE MESSAGES
        self.criticality = 0.0
        crit_neg = 0.0
        nb_exced_message = max(0, sum_weight - self.computing_capacity)
        pourcent_exced = nb_exced_message / self.computing_capacity * 100
        if pourcent_exced > THRESHOLD_TOO_MUCH_RECEIVED_MIN * 100:
            crit_neg = min(MAX_TMR, COEFF_A_TMR * pourcent_exced + COEFF_B_TMR)

        # MANAGE USELESS MESSAGES
        nb_useless, nb_useful, less_reliable = self.computeUselessMessage()
        self.crits[2] = crit_neg
        # useless_over_threshold = max(nb_useless - self.computing_capacity * THRESHOLD_TOO_MUCH_USELESS_MIN, 0)
        pourcent_useless = nb_useless / self.computing_capacity * 100

        # CCRIT
        # CRIT 3 -> TROP DE MESSAGES INUTILES
        # crit_neg = math.pow(nb_exced_message + useless_over_threshold, POW_BASE)
        crit_useless = 0
        if pourcent_useless > THRESHOLD_TOO_MUCH_USELESS_MIN * 100:
            crit_useless = min(MAX_TMU, COEFF_A_TMU * pourcent_useless + COEFF_B_TMU)
        usefull_missing = len(self.received_messages) - nb_useful
        self.crits[3] = crit_useless

        # CCRIT
        # CRIT 1 -> PAS ASSEZ DE MESSAGES INUTILES
        nb_envie = max(nb_useless - self.computing_capacity * THRESHOLD_NOT_ENOUGH_USELESS_MIN, 0)
        pourcent_envie = nb_useless / self.computing_capacity * 100
        nb_envie = min(nb_envie, usefull_missing)
        crit_pos = 0
        if pourcent_envie < THRESHOLD_NOT_ENOUGH_USELESS_MIN * 100:
            crit_pos = min(MAX_NE, COEFF_A_NE * pourcent_envie + COEFF_B_NE)
        self.crits[1] = crit_pos

        # CCRIT
        # CRIT 4 -> DIFFERENCE AVEC MEILLEUR SCORE
        max_diff_score = self.scores["max"] - self.scores["min"]
        crit_score = 0.0
        if self.scores["max"] > self.last_score:
            pourcent_diff = (self.scores["max"] - self.last_score) / max_diff_score
            crit_score = min(MAX_TS, COEFF_A_TS * pourcent_diff + COEFF_B_TS)
        crit_pos += crit_score
        # crit_pos = math.log(nb_envie, LOG_BASE)

        self.criticality = crit_pos - crit_neg - crit_useless

        self.to_send.append(MessageCrit(id_ag=self.id_ag, crit=self.criticality))
        print("NBUSELESS : " + str(nb_useless))
        if self.criticality < 0:
            print(str(self) + " -> too many messages received " + str(self.criticality))
        else:
            if self.criticality > 0:
                print(str(self) + " -> need messages please " + str(self.criticality))

        # when an information is no longer shared  because of an agent missing and i can share it, i share it
        # first we delete all the items
        self.received_messages.clear()
        # when i know nothing, I send the ones I know useful for me
        print("SIZE : " + str(len(self.decision_variable.keys())))
        cumul_weight = 0
        worst_crit = 0.0
        best_crit = 100.0
        for criticalities in self.received_crit:
            if criticalities.sender != self.id_ag and criticalities.sender in self.neighborhood.keys():
                if abs(worst_crit) < abs(criticalities.crit):
                    worst_crit = criticalities.crit
                if abs(best_crit) > abs(criticalities.crit):
                    best_crit = criticalities.crit
                self.neighborhood[criticalities.sender] =criticalities.crit
        '''if worst_crit < 0 or self.criticality == best_crit:
            if self.criticality > 0:
                self.communication_capacity -= 1
        if worst_crit > 0:
            if self.criticality < 0 or self.criticality == best_crit:
                self.communication_capacity += 1'''
        if worst_crit < 0:
            self.communication_capacity -= 1
        if worst_crit > 0:
            self.communication_capacity += 1
        self.received_crit.clear()

        # pour toutes les variables
        for var in self.decision_variable.keys():
            # si je suis encore capable d'en envoyer
            var_weight = self.decision_variable[var].size
            if var not in less_reliable and cumul_weight + var_weight < self.communication_capacity:
                self.to_send.append(Message(var, self.id_ag, self.decision_variable[var].size, 0.0))
                cumul_weight += var_weight

    def act(self):
        print("ACT PHASE " + str(self.id_ag))
        # send messages
        # print("TOSEND : -> " + str(self.to_send))
        # for var in self.to_send:
        #    messages.append(Message(var, self.id_ag, self.decision_variable[var].size, 0.0))
        self.network.sendMessages(self.to_send)

    def receive_messages(self, sent: [Message]):
        self.received_messages = sent

    def receive_message_from_netowrk(self):
        for mess in self.network.releaseMessages():
            if mess.sender != self.id_ag:
                if isinstance(mess, MessageCrit):
                    self.received_crit.append(mess)
                else:
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
        self.last_score = efficiency
        self.scores["max"] = max(self.last_score, self.scores["max"])
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
            if mess.sender != self.id_ag:
                if not isinstance(mess, MessageCrit):
                    if sum_weight <= self.computing_capacity and mess.name in var_used.keys():
                        if var_used[mess.name] < self.environment.distribution_gauss_sensed[mess.name][mess.sender]:
                            var_used[mess.name] = self.environment.distribution_gauss_sensed[mess.name][mess.sender]
                            sum_weight += mess.weight
        # compute the efficiency
        for var_name in var_used.keys():
            efficiency += var_used[var_name]

        self.last_score = efficiency
        self.scores["max"] = max(self.last_score, self.scores["max"])
        return int(efficiency)

    def computeUselessMessage(self) -> (int, int, []):
        best_messages = {}
        less_reliable = []
        nb_useless_message = 0
        nb_usefull = 0
        worst_crit = 0
        for mess in self.received_messages:
            # if isinstance(mess, MessageCrit):
            #     worst_crit = max(mess.crit, worst_crit)
            #     self.received_messages.remove(mess)
            # else:
            if mess.name in self.decision_variable.keys() and mess.sender in self.neighborhood.keys():
                var_tmp = self.analyse_message(mess)
                if var_tmp.reliability > self.decision_variable[mess.name].reliability:
                    if mess.name not in best_messages.keys():
                        best_messages[mess.name] = mess
                        nb_usefull += 1
                    else:
                        # CCRIT
                        nb_useless_message += 1

                        var_best = self.analyse_message(best_messages[mess.name])
                        if var_best.reliability < var_tmp.reliability:
                            best_messages[mess.name] = mess
                    if mess.name not in less_reliable:
                        less_reliable.append(mess.name)
                else:
                    # CCRIT
                    nb_useless_message += 1
            else:
                # CCRIT
                nb_useless_message += 1
        return nb_useless_message, nb_usefull, less_reliable

    def __str__(self):
        return "Agent " + str(self.id_ag) + " Criticality : " + str(self.criticality) + "\n" + str(self.crits) \
               + " CommCapa: " + str(self.communication_capacity)

    def __repr__(self):
        return str(self)
        # return "Agent " + str(self.id_ag) + " Criticality : " + str(self.criticality)
