from world.Amas import Amas
from oracles import pulpSolver
from oracles import VarWatcher
import sys

if __name__ == '__main__':
    print('BEGIN')
    scenario = "sc12"
    scenarios = ["sc5", "sc6", "sc7", "scenario_high_dynamic"]
    amas = Amas(experiment=scenario, explo=True)
    amas.__run__(300)

    '''pulpSolver.run(scenario)
    VarWatcher.compareVar(scenario)'''
    '''for sc in scenarios:
        amas = Amas(experiment=sc)
        amas.__run__(300)'''
    root = "scenario_dynamic_controlled/"
    # amas = Amas(root=root, experiment=sc)
    '''for sc in scenarios:
        for i in range(30):
            amas = Amas(experiment=sc, test=False, id=i)
            amas.__run__(300)'''
    sc = "scenario_30ag"
    # amas = Amas(experiment=sc)
    # amas.__run__(300)

    '''sc = "scdyn1"
    amas = Amas(root=root, experiment=sc)
    amas.__run__(300)'''
    '''for scenario in scenarios:
        pulpSolver.run(scenario)
        VarWatcher.compareVar(scenario)'''
