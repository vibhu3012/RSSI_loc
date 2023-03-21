from rssicore import *
from math import sqrt
from numpy import count_nonzero

class ENCODING:

    class ORIENTATION:
        NORTH = 0
        SOUTH = 1
        EAST = 2
        WEST = 3

    class ALG:

        # clustering algorithm
        MONO = "mono"

        # coarse localization
        USEALL = "useall"

        # estimator
        KNN = "knn"
        PROB = "prob"
        KMEANS = "kmeans"
        LASSO = "lasso"

        # AP selector
        NAIVE = "naive"
        FISHER = "fisher"

def wrapper(x):
    return int(x) if x else -100

def distance(a, b):
    assert len(a) == len(b)
    # debug("distance from " + str(a))
    # debug("to " + str(b))
    ret = 0
    for i, j in zip(a,b):
        ret += (wrapper(i) - wrapper(j)) ** 2
    return sqrt(ret)

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def hamming(a, b, LAMBDA):
    return 1 / (count_nonzero(a!=b) + LAMBDA)

    
