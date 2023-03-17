from rssicore import * # logging
from rssicore.Utils import ENCODING, distance

def estimator(rssi:list, rps:list, alg:str) -> list:
    """
    : return a list with the same length as ref
    : the probability of prediction estimation
    : sum(estimator) = 1
    """
    if alg == ENCODING.ALG.KNN:
        return KNN(rssi, rps)
    if alg == ENCODING.ALG.PROB:
        return prob(rssi, rps)
    raise ValueError

def KNN(rssi:list, rps:list, k:int = 4) -> list:
    ret = [0.] * len(rps)

    dist = []
    for rp in rps:
        dist.append(distance(rssi, rp))
    dist = list(enumerate(dist))
    dist.sort(key = lambda x: x[1])
    
    for i in range(k):
        ret[dist[i][0]] = 1/k
    return ret

def prob(rssi:list, rps:list, sigma:float = 2) -> list:
    print("not implemented")
    raise NotImplementedError

def est2loc(est:list, loc_ref:list):
    assert len(est) == len(loc_ref)
    locProb = list(zip(loc_ref, est))
    locProb.sort(reverse = True,
                 key = lambda x: x[1])
    # debug(locProb)
    genPrint = lambda x: "{}({})".format(x[0], x[1])
    return " ".join([genPrint(x) for x in locProb[:5]])