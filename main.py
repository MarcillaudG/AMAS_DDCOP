from world.Amas import Amas
from oracles import pulpSolver

if __name__ == '__main__':
    print('BEGIN')
    scenario = "scenario_30ag"
    amas = Amas(experiment=scenario)
    amas.__run__(100)
    pulpSolver.run(scenario)
