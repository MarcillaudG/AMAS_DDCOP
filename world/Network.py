
from agents.Messages import Message


class Network:
    capacity = None

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.messages = []

    def __cycleBegin__(self) -> None:
        self.messages.clear()

    def releaseMessages(self):
        return self.messages

    def sendMessages(self, messages_sent: [Message]) -> None:
        self.messages = self.messages+messages_sent

    def nb_messages(self):
        return len(self.messages)
