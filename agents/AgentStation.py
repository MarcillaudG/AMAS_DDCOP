import math
import random
from time import sleep

import numpy

from agents.Messages import Message, MessageCrit
from tool.AVT import AVT

from world.Environment import Environment
from world.Network import Network
from world.Variables import Variables

# TOO MUCH RECEIVED CRIT
THRESHOLD_TOO_MUCH_RECEIVED_MIN = 0.90
THRESHOLD_TOO_MUCH_RECEIVED_MAX = 1.00
MAX_TMR = 100.0
MIN_TMR = 0.0
COEFF_A_TMR = (MAX_TMR - MIN_TMR) / ((THRESHOLD_TOO_MUCH_RECEIVED_MAX - THRESHOLD_TOO_MUCH_RECEIVED_MIN) * 100)
COEFF_B_TMR = MAX_TMR - COEFF_A_TMR * (THRESHOLD_TOO_MUCH_RECEIVED_MAX * 100)
print("COEFF_A_TMR : " + str(COEFF_A_TMR) + " COEFF_B_TMR : " + str(COEFF_B_TMR))

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

# IMPROVEMENT THRESHOLD
IMPROVEMENT_THRESHOLD = 5.0
REPLACING_BONUS = 2.0



class AgentStation:
    id_ag = None

    def __init__(self, id_ag: int, computing_capacity: int, communication_capacity: int,
                 environment: Environment, network: Network, com_range=999999):
        self.id_ag = id_ag
        self.criticality = 0.0
        self.crits = {1: 0.0, 2: 0.0, 3: 0.0}
        self.environment = environment
        self.network = network
        self.com_range = com_range
        self.var = {}
        self.neighborhood = {}
        self.decision_variable = {}
        self.computing_capacity = computing_capacity
        self.communication_capacity = communication_capacity
        self.useless_variable = []
        self.to_send = []
        self.to_replace = []
        self.sent = []
        self.received_messages = []
        self.received_crit = []
        self.last_crit_sent = 0.0
        self.last_score = 0
        self.last_worst_crit = 0.0
        self.scores = {"min": 0, "max": 0}
        self.nb_messages_sent = 0
        self.avt = AVT(IMPROVEMENT_THRESHOLD)
        self.improv = IMPROVEMENT_THRESHOLD
        self.__initUtility__()

    def __initUtility__(self):
        for env_var in self.environment.variables.keys():
            utility = self.environment.getReliability(env_var, self.id_ag)
            if utility >= 2:
                self.decision_variable[env_var] = Variables(env_var, utility, self.environment.variables[env_var].size)
        score = self.computeEfficiencyLimit()
        print("LEN DV : " + str(len(self.decision_variable.keys())))
        self.scores["min"] = score
        self.scores["max"] = score
        self.last_score = score
        self.impact_com_neg = 1 / self.computing_capacity * (COEFF_A_TMR + COEFF_A_TMU)
        self.impact_com_pos = 1 / self.computing_capacity * COEFF_A_NE

    def perceive(self, neighbors: []):
        # print("PERCEIVE PHASE " + str(self.id_ag))

        # perceive my neighbours
        new_dict = {}
        for new_neighbour in neighbors:
            new_dict[new_neighbour] = 0.0
            if new_neighbour in self.neighborhood.keys():
                new_dict[new_neighbour] = self.neighborhood[new_neighbour]
        self.neighborhood = new_dict
        self.receive_criticalities_from_network()
        # what my sensors gather
        # not used for now
        self.sent = []
        for mess in self.to_send:
            self.sent.append(mess.name)
        self.communication_capacity = len(self.sent)
        self.to_send.clear()
        self.to_replace.clear()
        # perceive the variable sorted by reliability
        self.decision_variable = dict(sorted(self.decision_variable.items(), key=lambda item: item[1], reverse=True))
        # self.impact_com_neg = 1 / self.computing_capacity * (COEFF_A_TMR + COEFF_A_TMU) * len(self.neighborhood.keys())
        # self.impact_com_neg = 1 / self.computing_capacity * (COEFF_A_TMR) * len(self.neighborhood.keys())
        self.impact_com_neg = self.comput_crit_neg(round(THRESHOLD_TOO_MUCH_RECEIVED_MIN * self.computing_capacity) + 1)
        if self.impact_com_neg == 0:
            print("bla")
        # self.impact_com_pos = 1 / self.computing_capacity * COEFF_A_NE * len(self.neighborhood.keys())
        self.impact_com_pos = self.comput_crit_pos(1)
        # print(str(self.impact_com))

    def decide(self):
        # print("DECIDE PHASE " + str(self.id_ag))
        # compute the best variable to send (to put at 1)
        nb_useless, nb_useful, less_reliable, more_reliable = self.computeUselessMessage()

        # MANAGE USELESS MESSAGES
        # when an information is no longer shared  because of an agent missing and i can share it, i share it
        # first we delete all the items
        self.received_messages.clear()
        # when i know nothing, I send the ones I know useful for me
        # print("SIZE : " + str(len(self.decision_variable.keys())))
        worst_crit = 0.0
        best_crit = 100.0
        for criticalities in self.received_crit:
            if criticalities.sender != self.id_ag and criticalities.sender in self.neighborhood.keys():
                # if abs(worst_crit) < abs(criticalities.crit):
                #    worst_crit = criticalities.crit
                # if best_crit > abs(criticalities.crit):
                #    best_crit = abs(criticalities.crit)
                self.neighborhood[criticalities.sender] = criticalities.crit

        for other_ag in self.neighborhood.keys():
            criticalities = self.neighborhood[other_ag]
            if abs(worst_crit) < abs(criticalities):
                worst_crit = criticalities
            if best_crit > abs(criticalities):
                best_crit = abs(criticalities)

        self.histoAVT(worst_crit)
        nb_tour = 0
        if abs(worst_crit) < self.improv:
            self.improv = abs(worst_crit)
        if abs(worst_crit) > IMPROVEMENT_THRESHOLD:
            self.improv = IMPROVEMENT_THRESHOLD
        nb_message_needed = 0
        if worst_crit > 0:
            nb_message_needed = self.improv / self.impact_com_pos
        else:
            nb_message_needed = self.improv / self.impact_com_neg
        cut_improv = nb_message_needed / len(self.neighborhood)
        #if abs(worst_crit) >= IMPROVEMENT_THRESHOLD:

        if abs(worst_crit) >= self.improv and self.analyse_effect(worst_crit, -numpy.sign(worst_crit)):
            improvement = 0.0
            # while improvement <= IMPROVEMENT_THRESHOLD:
            # while self.analyse_effect(worst_crit, -numpy.sign(worst_crit),
            # improvement) and improvement <= self.improv:
            while improvement < cut_improv:
                if worst_crit < 0:
                    impact_reduce = COEFF_A_TMR + COEFF_A_TMU

                    tirage = random.random()
                    # if tirage * 100 < IMPROVEMENT_THRESHOLD:
                    if tirage < cut_improv - improvement:
                        if self.communication_capacity > 0:
                            self.communication_capacity -= 1
                        self.avt.clean()
                    improvement += abs(self.impact_com_neg)
                        # if self.criticality > 0 or abs(self.criticality) <= best_crit:
                    #     self.communication_capacity = max(0, self.communication_capacity - 1)
                if worst_crit > 0:
                    impact_reduce = COEFF_A_NE
                    tirage = random.random()
                    # if tirage * 100 < IMPROVEMENT_THRESHOLD:
                    if len(more_reliable) > 0:
                        tirage = tirage / REPLACING_BONUS
                    if tirage < cut_improv - improvement:
                        if self.communication_capacity < len(self.decision_variable.keys()) - len(less_reliable):
                            self.communication_capacity += 1
                        self.avt.clean()

                    improvement += abs(self.impact_com_pos)
                nb_tour += 1
                        # if self.criticality < 0 or abs(self.criticality) <= best_crit:
                #    self.communication_capacity = min(len(self.decision_variable.keys()), self.communication_capacity + 1)
        '''if worst_crit < 0:
            self.communication_capacity -= 1
        if worst_crit > 0:
            self.communication_capacity += 1'''
        self.received_crit.clear()
        self.last_worst_crit = worst_crit
        # for var in more_reliable:
        #    var_weight = self.decision_variable[var].size
        #    if cumul_weight + var_weight <= self.communication_capacity:
        #        self.to_send.append(Message(var, self.id_ag, self.decision_variable[var].size, 0.0))
        #        cumul_weight += var_weight
        self.decideMessageToSend(less_reliable, more_reliable)
        # pour toutes les variables

    def act(self):
        # print("ACT PHASE " + str(self.id_ag))
        # send messages
        # print("TOSEND : -> " + str(self.to_send))
        # for var in self.to_send:
        #    messages.append(Message(var, self.id_ag, self.decision_variable[var].size, 0.0))
        self.network.sendMessages(self.to_send)
        self.nb_messages_sent = len(self.to_send)

    # look if acting does not create a new worst critical worst than before
    def analyse_effect(self, worst_crit: float, action: int) -> bool:
        for criticalities in self.received_crit:
            if criticalities.sender != self.id_ag and criticalities.sender in self.neighborhood.keys():
                new_crit = 0
                if criticalities.crit < 0 and action == -1:
                    new_crit = abs(criticalities.crit) + self.improv
                if criticalities.crit > 0 and action == 1:
                    new_crit = abs(criticalities.crit) + self.improv
                if new_crit > abs(worst_crit):
                    return False
                # if criticalities
        return True

    def receive_messages(self, sent: [Message]):
        self.received_messages = sent

    # The agent decides which variables send
    def decideMessageToSend(self, less_reliable: [], more_reliable: []) -> None:
        cumul_weight = 0
        # What was sent is still sent unless it is less relaible
        var_to_sent = []
        for var in self.sent:
            var_weight = self.decision_variable[var].size
            if var not in less_reliable:
                if cumul_weight + var_weight <= self.communication_capacity:
                    self.to_send.append(Message(var, self.id_ag, self.decision_variable[var].size, 0.0))
                    cumul_weight += var_weight
                    var_to_sent.append(var)

        # I know that i am better, so if I have room i send in priority
        if cumul_weight < self.communication_capacity:
            for var in more_reliable:
                var_weight = self.decision_variable[var].size
                if var not in less_reliable and var not in self.sent:
                    if cumul_weight + var_weight <= self.communication_capacity:
                        self.to_send.append(Message(var, self.id_ag, self.decision_variable[var].size, 0.0))
                        cumul_weight += var_weight
                        if var in var_to_sent:
                            print("ERROR 1")
                        var_to_sent.append(var)


        # If i don t have any idea, trust myself
        if cumul_weight < self.communication_capacity:
            i = 0
            while i < len(self.decision_variable) and cumul_weight < self.communication_capacity:
                var = list(self.decision_variable.keys())[i]
                # si je suis encore capable d'en envoyer
                var_weight = self.decision_variable[var].size
                if var not in less_reliable and var not in self.sent and var not in more_reliable:
                    if cumul_weight + var_weight <= self.communication_capacity:
                        self.to_send.append(Message(var, self.id_ag, self.decision_variable[var].size, 0.0))
                        cumul_weight += var_weight
                        if var in var_to_sent:
                            print("ERROR 2")
                        var_to_sent.append(var)
                i += 1

    # Receives messages sent by neighbors
    def receive_message_from_netowrk(self):
        for mess in self.network.releaseMessages():
            if mess.sender != self.id_ag and mess.sender in self.neighborhood:
                if isinstance(mess, MessageCrit):
                    self.received_crit.append(mess)
                else:
                    self.received_messages.append(mess)

    # Receives criticalities from neighbors
    def receive_criticalities_from_network(self):
        for mess in self.network.releaseMessagesCrit():
            if mess.sender != self.id_ag:
                if isinstance(mess, MessageCrit):
                    self.received_crit.append(mess)

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
            var_used[env_var] = 0.0

        # select the best messages in the receive order
        # if it cannot compute more, it doest treat anymore
        for mess in self.received_messages:
            if mess.sender != self.id_ag:
                if not isinstance(mess, MessageCrit):
                    if sum_weight <= self.computing_capacity and mess.name in var_used.keys():
                        if var_used[mess.name] < self.environment.distribution_gauss_sensed[mess.name][mess.sender]:
                            var_used[mess.name] = self.environment.distribution_gauss_sensed[mess.name][mess.sender]
                            sum_weight += mess.weight
            else:
                if var_used[mess.name] < self.environment.distribution_gauss_sensed[mess.name][mess.sender]:
                    var_used[mess.name] = self.environment.distribution_gauss_sensed[mess.name][mess.sender]
                    sum_weight += mess.weight
        # compute the efficiency
        for var_name in var_used.keys():
            efficiency += var_used[var_name]

        self.last_score = efficiency
        self.scores["max"] = max(self.last_score, self.scores["max"])
        return int(efficiency)

    def computeUselessMessage(self) -> (int, int, [], []):
        best_messages = {}
        less_reliable = []
        more_reliable = []
        nb_useless_message = 0
        nb_usefull = 0
        for mess in self.received_messages:
            # if isinstance(mess, MessageCrit):
            #     worst_crit = max(mess.crit, worst_crit)
            #     self.received_messages.remove(mess)
            # else:
            if mess.sender in self.neighborhood.keys():
                if mess.name in self.decision_variable.keys():
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
                        if mess.name in more_reliable:
                            more_reliable.remove(mess.name)
                    else:
                        # CCRIT
                        nb_useless_message += 1
                        if mess.name not in less_reliable and mess.name not in more_reliable:
                            more_reliable.append(mess.name)
                else:
                    # CCRIT
                    nb_useless_message += 1
        return nb_useless_message, nb_usefull, less_reliable, more_reliable

    # compute the agent criticality
    def computeCriticality(self) -> None:
        # Manage criticality
        sum_weight = 0
        for mess in self.received_messages:
            if mess.sender != self.id_ag:
                sum_weight += mess.weight
        # CCRIT
        # CRIT 2 -> TROP DE MESSAGES
        old_crit = self.criticality
        self.criticality = 0.0
        crit_neg = 0.0
        # nb_exced_message = max(0, sum_weight - self.computing_capacity)
        # pourcent_exced = nb_exced_message / self.computing_capacity * 100
        pourcent_exced = sum_weight / self.computing_capacity * 100
        if pourcent_exced > THRESHOLD_TOO_MUCH_RECEIVED_MIN * 100:
            crit_neg = min(MAX_TMR, COEFF_A_TMR * pourcent_exced + COEFF_B_TMR)

        # MANAGE USELESS MESSAGES
        nb_useless, nb_useful, less_reliable, more_reliable = self.computeUselessMessage()
        self.nb_useless = nb_useless
        self.crits[2] = crit_neg
        # useless_over_threshold = max(nb_useless - self.computing_capacity * THRESHOLD_TOO_MUCH_USELESS_MIN, 0)
        pourcent_useless = nb_useless / self.computing_capacity * 100

        # CCRIT
        # CRIT 3 -> TROP DE MESSAGES INUTILES
        # crit_neg = math.pow(nb_exced_message + useless_over_threshold, POW_BASE)
        crit_useless = 0
        '''if pourcent_useless > THRESHOLD_TOO_MUCH_USELESS_MIN * 100:
            crit_useless = min(MAX_TMU, COEFF_A_TMU * pourcent_useless + COEFF_B_TMU)'''
        usefull_missing = len(self.received_messages) - nb_useful
        self.crits[3] = crit_useless

        # CCRIT
        # CRIT 1 -> PAS ASSEZ DE MESSAGES INUTILES
        pourcent_envie = nb_useless / self.computing_capacity * 100
        taux_envie = 0.0
        if pourcent_envie < THRESHOLD_NOT_ENOUGH_USELESS_MIN * 100:
            taux_envie = min(MAX_NE, COEFF_A_NE * pourcent_envie + COEFF_B_NE)
        # crit_pos = taux_envie * max(0, (self.computing_capacity - sum_weight) / self.computing_capacity)
        crit_pos = taux_envie
        self.crits[1] = crit_pos

        # CCRIT
        # CRIT 4 -> DIFFERENCE AVEC MEILLEUR SCORE
        max_diff_score = self.scores["max"] - self.scores["min"]
        crit_score = 0.0
        if self.scores["max"] > self.last_score:
            pourcent_diff = (self.scores["max"] - self.last_score) / max_diff_score
            crit_score = min(MAX_TS, COEFF_A_TS * pourcent_diff + COEFF_B_TS)
        # crit_pos += crit_score

        self.criticality = crit_pos - crit_neg - crit_useless

        worst_crit = 0.0
        worst_not_abs = 0.0
        for other_ag in self.neighborhood.keys():
            if abs(self.neighborhood[other_ag]) > worst_crit:
                worst_crit = abs(self.neighborhood[other_ag])
                worst_not_abs = self.neighborhood[other_ag]
        # print("OLD : " + str(self.last_crit_sent)  + " WORST : " + str(worst_not_abs) + "  self : " + str(self.criticality))
        '''if abs(self.last_crit_sent) >= abs(self.last_worst_crit) or abs(self.criticality) >= abs(worst_crit)\
                or abs(self.last_crit_sent) >= abs(worst_crit) or abs(self.criticality) > abs(self.last_crit_sent):
            self.network.sendCriticality(MessageCrit(id_ag=self.id_ag, crit=self.criticality))
            self.last_crit_sent = self.criticality'''
        self.network.sendCriticality(MessageCrit(id_ag=self.id_ag, crit=self.criticality))
        # print("NBUSELESS : " + str(nb_useless))

    '''Compute the criticality neg according to the number of messages received'''
    def comput_crit_neg(self, nb_messages: int):
        res = 0
        if nb_messages > self.computing_capacity * THRESHOLD_TOO_MUCH_RECEIVED_MIN:
            res = COEFF_A_TMR * nb_messages / self.computing_capacity * 100 + COEFF_B_TMR
        return res

    '''Compute the criticality pos according to the number of useless messages received'''
    def comput_crit_pos(self, nb_messages_useless: int):
        res = 0
        if nb_messages_useless > 0:
            res = 100 - (COEFF_A_NE * nb_messages_useless / self.computing_capacity * 100 + COEFF_B_NE)
        return res

    def histoAVT(self, worst_crit: float):
        if worst_crit > 0 and self.last_worst_crit < 0:
            self.avt.clean()
        if worst_crit < 0 and self.last_worst_crit > 0:
            self.avt.clean()
        histo = worst_crit
        if histo < 0:
            histo = -1
        if histo > 0:
            histo = 1
        self.avt.add_histo(histo)

    def __str__(self):
        return "Agent " + str(self.id_ag) + " Criticality : " + str(self.criticality) + "\n" + str(self.crits) \
               + " CommCapa: " + str(self.communication_capacity)

    def strID(self):
        if self.id_ag < 10:
            return "00" + str(self.id_ag)
        if self.id_ag < 100:
            return "0" + str(self.id_ag)
        return str(self.id_ag)

    def strCrit(self):
        if abs(self.criticality) < 10:
            return "00" + str(int(abs(self.criticality)))
        if abs(self.criticality) < 100:
            return "0" + str(int(abs(self.criticality)))
        return str(int(abs(self.criticality)))

    def __repr__(self):
        return str(self)
        # return "Agent " + str(self.id_ag) + " Criticality : " + str(self.criticality)

    def getComputingCapacity(self):
        return self.computing_capacity



