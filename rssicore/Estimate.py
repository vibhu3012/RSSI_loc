from rssicore import * # logging
from rssicore.Utils import ENCODING, distance, wrapper

from scipy.stats import norm
import scipy.stats as stats
from math import log, exp

def estimator(rssi:list, rps:dict, alg:str):
    """
    : return a list with the same length as ref
    : the probability of prediction estimation
    : sum(estimator) = 1
    """
    if alg == ENCODING.ALG.KNN:
        return KNN(rssi, rps)
    if alg == ENCODING.ALG.PROB:
        return prob(rssi, rps)
    if alg == ENCODING.ALG.LASSO:
        return lasso(rssi, rps)
    raise ValueError

def merge(rps):
    # merge the last DoF 
    merged = {}
    getLoc = lambda x: ".".join(x.split(".")[0:3])
    for label in rps.keys():
        loc = getLoc(label)
        rssi_value = rps[label]
        if loc in merged.keys():
            assert len(merged[loc]) == len(rssi_value)
            for ap, rv in zip(merged[loc], rssi_value):
                ap.append(rv)
            continue
        else:
            merged[loc] = []
            for ap in rssi_value:
                merged[loc].append([ap])
    return merged

def KNN(rssi:list, rps:dict, k:int = 4):

    # merge the last DoF 
    merged = merge(rps)

    avg = lambda l: sum([wrapper(i) for i in l]) / len(l)
    avgWrapper = lambda x: [avg(ap) for ap in x]

    dist = {}
    for loc, rp in merged.items():
        # dist[loc] = 1 / (distance(rssi, avgWrapper(rp)) + 1e-2)
        dist[loc] = - distance(rssi, avgWrapper(rp))

    return dist.values(), dist.keys()

def prob(rssi:list, rps:dict):

    # merge the last DoF 
    merged = merge(rps)

    # first = list(merged.keys())[0]
    # debug(merged[first])
    for loc, aps in merged.items():
        new_aps = []
        for ap in aps:
            float_list = list(map(wrapper, ap))
            mu, sigma = norm.fit(float_list)
            new_aps.append( (mu, sigma) )
        merged[loc] = new_aps
    # debug(merged[first])

    sigmaWrapper = lambda x: max(x, 1e-1)
    # probAP = lambda x, mu, sigma: stats.norm(mu, sigmaWrapper(sigma)).pdf(x)
    probAP_log = lambda x, mu, sigma: \
        - log(sigmaWrapper(sigma)) - 1/2 * ((x-mu)/sigmaWrapper(sigma)) ** 2
    scores = []
    for meas in merged.values():
        score = 0.
        for rv, ap_mea in zip(rssi, meas):
            score += probAP_log(wrapper(rv), ap_mea[0], ap_mea[1])
        scores.append(score/1e4)

    # value difference toolarge
    # unified = []
    # for si in scores:
    #     sum = 0.
    #     try:
    #         for sj in scores: 
    #             sum += exp(sj-si)
    #     except OverflowError:
    #         unified.append(0)
    #         continue
    #     unified.append(1/sum)
    return scores, merged.keys()

def lasso(rssi:list, rps:dict):
    print("not implemented")
    raise NotImplementedError

def est2loc(est:list, loc_ref:list):
    assert len(est) == len(loc_ref)
    locProb = list(zip(loc_ref, est))
    locProb.sort(reverse = True,
                 key = lambda x: x[1])
    # debug(locProb)
    genPrint = lambda x: "{}({:.2f})".format(x[0], x[1])
    return " ".join([genPrint(x) for x in locProb[:8]])