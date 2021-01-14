from tool import constraints_tools as ct


class AgFunction:

    def __init__(self):
        self.var = []
        self.conditions = {}

    def add_var(self, var : str):
        if var not in self.var:
            self.var.append(var)

    def add_condition(self, name, symbol, value, reward_good, reward_bad):
        self.conditions[name] = (symbol, value, reward_good, reward_bad)

    def remove_condition(self, name):
        self.conditions.remove(name)

    def evaluate_function(self, var_value):
        res = 0.0
        for condition in self.conditions:
            res += ct.evaluate_condition(condition, var_value)
        return res
