
def cluster(rps:dict, alg:str) -> dict:
    # TODO 
    return monoClustering(rps)

def monoClustering(rps) -> dict:
    '''
    cluster all into a big cluster
    '''
    member = list(rps.keys())
    head = member[0]
    return {head : member}


def coarseLoc(rssi:list, rps:dict, clustering:dict) -> dict:
    # TODO
    return coarseLocFull(rssi, rps)

def coarseLocFull(rssi, rps) -> dict:
    '''
    use all rps
    '''
    return rps
