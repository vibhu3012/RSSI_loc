from rssicore import *
from math import sqrt

class ENCODING:

    class ORIENTATION:
        NORTH = 0
        SOUTH = 1
        EAST = 2
        WEST = 3

    class ALG:

        # estimator
        KNN = "knn"
        PROB = "prob"
        KMEANS = "kmeans"

        # AP selector
        NAIVE = "naive"
        FISHER = "fisher"

def distance(a, b):
    assert len(a) == len(b)
    # debug("distance from " + str(a))
    # debug("to " + str(b))
    wrapper = lambda x: int(x) if x else -100
    ret = 0
    for i, j in zip(a,b):
        ret += (wrapper(i) - wrapper(j)) ** 2
    return sqrt(ret)
    
