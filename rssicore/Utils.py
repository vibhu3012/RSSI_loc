from math import sqrt

class ENCODING:
    class ORIENTATION:
        NORTH = 0
        SOUTH = 1
        EAST = 2
        WEST = 3
    class ALG:
        KNN = "knn"
        PROB = "prob"
        KMEANS = "kmeans"
        FISHER = "fisher"

def distance(a, b):
    assert len(a) == len(b)
    wrapper = lambda x: x if x else -100
    ret = 0
    for i, j in zip(a,b):
        ret += (wrapper(i) - wrapper(j)) ** 2
    return sqrt(ret)
    
