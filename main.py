from world.Amas import Amas

if __name__ == '__main__':
    print('BEGIN')
    amas = Amas(experiment="scenario_30ag")
    amas.__run__(100)
