from pulp import *

if __name__ == '__main__':
    print("SOLVING BEGIN")
    file_name = "scenario_test_yaml.yaml"
    file = open("../DCOP/" + file_name, "r")
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
                            print("LA" + str(all_var_split[i].split("\n")[0]))
                            all_var_in_constraint.append(all_var_split[i].split("\n")[0])
                        else:
                            print("ba" + all_var_split[i])
                            all_var_in_constraint.append(all_var_split[i])
            if "return" in line:
                split_coma = line.split(",")
                capa = split_coma[0][len(split_coma[0]) - 1]
                print("ICI" + str(all_var_in_constraint))
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
                    util[vn] = float(value)

                    if vn not in already_added:
                        already_added[vn] = float(value)
                model += lpSum([dict_vars[vn] for vn in di.keys()]) <= 1, name_constraint
    model += lpSum([dict_vars[vn] * util[vn] for vn in already_added.keys()]), "obj"
    model.writeLP("SocialCAV.lp")
    print(str(model.variables()))
    model.solve()

    print("Status:", LpStatus[model.status])

    for v in model.variables():
        print(v.name, "=", v.varValue)

    print("SCORE : ", value(model.objective))