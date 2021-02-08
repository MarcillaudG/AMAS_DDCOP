SIZE_HISTO = 10


class AVT:
    def __init__(self, score_init: float):
        self.histos = []
        self.delta = 1.0
        self.score = score_init
        self.acc = 2.0
        self.decc = 1.0 / 3.0
        self.ind_histo = 0

    def add_histo(self, value: int):
        if len(self.histos) < SIZE_HISTO:
            self.histos.append(value)
        else:
            self.histos[self.ind_histo] = value
        self.ind_histo = (self.ind_histo + 1) % SIZE_HISTO

        if len(self.histos) > 1:
            last_histo = self.ind_histo - 1
            if last_histo < 0:
                last_histo = SIZE_HISTO -1
            if value == -1:
                if self.histos[last_histo] == -1:
                    self.delta = self.delta * self.acc
                    self.score -= self.delta
                if self.histos[last_histo] == 0:
                    self.score -= self.delta
                if self.histos[last_histo] == 1:
                    self.delta = self.delta * self.decc
                    self.score -= self.delta
            if value == 0:
                self.delta = self.delta * self.decc
            if value == 1:
                if self.histos[last_histo] == -1:
                    self.delta = self.delta * self.decc
                if self.histos[last_histo] == 0:
                    self.score += self.delta
                if self.histos[last_histo] == 1:
                    self.delta = self.delta * self.acc
                    self.score += self.delta

    def clean(self):
        self.histos.clear()
        self.delta = 1.0
        self.score = 5.0
        self.acc = 2.0
        self.decc = 1.0 / 3.0
        self.ind_histo = 0

    def __str__(self):
        return "DELTAT: " + str(self.delta) + " SCORE: " + str(self.score)

    def __repr__(self):
        return str(self)