class OracleOneNetwork:

    def __init__(self):
        self.max_score = 0.0
        self.comput_max_score = 0
        self.best_score = 0.0
        # {id_ag: [Variables]}
        self.allocations = {}

    def computeScores(self, agents: []):
        for agent in agents:
            self.allocations[agent.id_ag] = []
            