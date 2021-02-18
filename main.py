from world.Amas import Amas
from oracles import pulpSolver
from oracles import VarWatcher

if __name__ == '__main__':
    print('BEGIN')
    scenario = "scenario1"
    amas = Amas(experiment=scenario)
    amas.__run__(100)
    pulpSolver.run(scenario)
    VarWatcher.compareVar(scenario)