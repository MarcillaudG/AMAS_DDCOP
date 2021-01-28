
from agents.Messages import Message, MessageCrit


class Network:
    capacity = None

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.messages = []
        self.messages_crit = []

    def __cycleBegin__(self) -> None:
        self.messages.clear()

    def __cycleEnd__(self) -> None:
        self.messages_crit.clear()

    def releaseMessages(self) -> []:
        return self.messages

    def releaseMessagesCrit(self) -> []:
        return self.messages_crit

    def sendMessages(self, messages_sent: [Message]) -> None:
        self.messages = self.messages+messages_sent

    def nb_messages(self):
        return len(self.messages)

    def sendCriticality(self, mess: MessageCrit):
        self.messages_crit.append(mess)
