from world.Amas import Amas
from oracles import pulpSolver
from oracles import VarWatcher

if __name__ == '__main__':
    print('BEGIN')
    scenario = "scenario_neighb"
    amas = Amas(experiment=scenario)
    amas.__run__(300)
    pulpSolver.run(scenario)
    VarWatcher.compareVar(scenario)