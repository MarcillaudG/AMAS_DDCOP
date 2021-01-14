# condition = (name, symbol, value, reward_good, reward_bad)
# (str, str, number, number, number)
# var_value = number
# compare var_value with value
def evaluate_condition(condition, var_value):
    (name, symbol, value, reward_good, reward_bad) = condition
    if symbol == "<":
        if var_value < value:
            return reward_good
        else:
            return reward_bad
    if symbol == "<=":
        if var_value < value:
            return reward_good
        else:
            return reward_bad
    if symbol == ">":
        if var_value > value:
            return reward_good
        else:
            return reward_bad
    if symbol == ">=":
        if var_value >= value:
            return reward_good
        else:
            return reward_bad
    if symbol == "=":
        if var_value == value:
            return reward_good
        else:
            return reward_bad
    if symbol == "!=":
        if var_value != value:
            return reward_good
        else:
            return reward_bad
    print("Condition " + condition + " not evaluated")
    return 0
