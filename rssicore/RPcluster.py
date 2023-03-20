from rssicore.Utils import ENCODING

def cluster(rps:dict, alg:str) -> dict:
    if alg == ENCODING.ALG.MONO:
        return monoClustering(rps)
    raise ValueError

def monoClustering(rps) -> dict:
    '''
    cluster all into a big cluster
    '''
    member = list(rps.keys())
    head = member[0]
    return {head : member}


def coarseLoc(rssi:list, rps:dict, clustering:dict, alg:str) -> dict:
    if alg == ENCODING.ALG.USEALL:
        return useall(rps)
    raise ValueError

def useall(rps) -> dict:
    '''
    use all rps
    '''
    return rps
