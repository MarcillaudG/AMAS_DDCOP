def compareVar(scenario: str) -> None:
    file_pulp = open("oracles/result_" + scenario + ".yaml.csv", "r")
    file_network = open("logs/" + scenario + "_network.csv", "r")
    file_result = open("oracles/varWatch" + scenario + ".csv", "w")
    file_result.write("Cycle;Sum_good;Sum_bad;Missing\n")
    var_pulp = []
    for line in file_pulp.readlines():
        if "_var" in line[:4]:
            line_rmf_split = line[1:].split(";")
            if "1.0" in line_rmf_split[1]:
                var_pulp.append(line_rmf_split[0])
    print(str(var_pulp))
    for line in file_network.readlines():
        line_split = line[:len(line)-2].split(";")
        cycle = line_split[0]
        sum_good = 0
        sum_bad = 0
        for i in range(1, len(line_split)):
            if line_split[i] in var_pulp:
                sum_good += 1
            else:
                sum_bad += 1
        file_result.write(cycle + ";" + str(sum_good) + ";" + str(sum_bad) + ";" + str(len(var_pulp) - sum_good) + "\n")

    file_pulp.close()
    file_network.close()
    file_result.close()