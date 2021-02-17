from pulp import *


def run(scenario: str) -> None:
    print("SOLVING BEGIN")
    file_name = scenario + ".yaml"
    file = open("DCOP/" + file_name, "r")
    variables = {}

    switch = 0
    model = LpProblem("SocialCAV", LpMaximize)
    name_constraint = "None"
    var_constraint = []
    already_added = {}
    dict_vars = {}
    util = {}
    cn = ""
    all_var_in_constraint = []
    for line in file.readlines():
        line_split = line.split(":")

        # CASES
        # Objective
        # if "objective" in line_split[0]:
        #    model = pulp.LpProblem(file, pulp.LpMaximize)

        if switch == 0:
            if "variables" in line_split[0]:
                switch = 1

        if switch == 1:
            if "var" in line_split[0] and "variables" not in line_split[0]:
                var_name = line_split[0].lstrip()
                variables[var_name] = LpVariable(var_name, lowBound=0, upBound=1, cat="Integer")

            if "constraints" in line_split[0]:
                switch = 2
                dict_vars = LpVariable.dicts("", variables.keys(), lowBound=0, upBound=1, cat="Integer")
                print(str(dict_vars.keys()))
        if "agents" in line:
            switch = 4
        if switch == 2 and "constraints" not in line_split[0]:
            print(line)
            if "congestion" in line_split[0] or "C_utility" in line_split[0]:
                name_constraint = line_split[0].lstrip()
                all_var_in_constraint.clear()
            if "a=" in line:
                all_var_split = line.split(" ")
                for i in range(1, len(all_var_split)):
                    if "var" in all_var_split[i]:
                        if "\n" in all_var_split[i]:
                            all_var_in_constraint.append(all_var_split[i].split("\n")[0])
                        else:
                            all_var_in_constraint.append(all_var_split[i])
            if "return" in line:
                split_coma = line.split(",")
                split_coma_minus = split_coma[0].split("-")[2]
                capa = split_coma_minus.lstrip()
                model += lpSum([dict_vars[vn] for vn in all_var_in_constraint]) <= int(capa), name_constraint

            if "C_utili" in line:
                cn = line_split[0].lstrip()

            if "[" in line:
                tmp = line[23:]
                tmp = tmp[:len(tmp) - 5]
                split_coma = tmp.split(",")
                di = {}
                for i in range(len(split_coma)):
                    split_times = split_coma[i].split("*")
                    vn = split_times[0].lstrip()
                    vn = vn.split(" ")[0]
                    value = split_times[1].lstrip()
                    di[vn] = float(value)
                    if vn in util.keys():
                        util[vn] += float(value)
                    else:
                        util[vn] = float(value)

                    if vn not in already_added:
                        already_added[vn] = float(value)
                model += lpSum([dict_vars[vn] for vn in di.keys()]) <= 1, name_constraint
    model += lpSum([dict_vars[vn] * util[vn] for vn in already_added.keys()]), "obj"
    model.writeLP("oracles/SocialCAV.lp")
    print(str(model.variables()))
    model.solve()

    print("Status:", LpStatus[model.status])

    file_result = open("oracles/result_" + file_name + ".csv", "w")
    result = 0.0
    sum_message = 0
    for v in model.variables():
        print(v.name, "=", v.varValue)
        file_result.write(v.name + ";" + str(v.varValue) + "\n")
        result += v.varValue * util[v.name[1:]]
        sum_message += v.varValue
    file_result.write(str(model.objective) + "\n")
    file_result.write(str(result) + "\n")
    file_result.write(str(sum_message))
    file_result.close()

    file.close()


if __name__ == '__main__':
    print("SOLVING BEGIN")
    file_name = "scenario1.yaml"
    run(file_name)
