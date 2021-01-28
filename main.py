from world.Amas import Amas

if __name__ == '__main__':
    print('BEGIN')
    amas = Amas(experiment="scenario1", init_ag=9)
    amas.__run__(100)
