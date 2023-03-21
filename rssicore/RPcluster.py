from rssicore.Utils import ENCODING

def cluster(rps:dict, ap_list:list, conf:dict) -> dict:
    if conf["RP_CLUSTER_ALG"] == ENCODING.ALG.MONO:
        return monoClustering(rps)
    elif conf["RP_CLUSTER_ALG"] == ENCODING.ALG.TRAD:
        return RPClustering(rps, ap_list, conf)
    raise ValueError



def RPClustering(d, ap_list, conf):

    GAMMA = -80  #Threshold above whcih an AP readig is too small
    M = 2 #How many of the 5 time readings does the AP value need to be above GAMMA
    LAMBDA = 1 / 1000 #Specifies a small amount to be added to hamming distance denominator to avoid zero division error
    ETA = 0.02
    DIRECTIONS =  ['north', 'south', 'east', 'west']

    import pandas as pd
    from rssicore.Utils import find_nth, hamming
    import numpy as np
    import collections

    AP_LIST = ap_list
    AP_MAP = {AP_LIST[i] : i for i in range(len(AP_LIST))}
    NUM_RECORDS = len(d)
    
    df = pd.DataFrame(AP_LIST, columns = ['AP'])
    temp = pd.DataFrame(d.values()).transpose()
    temp.columns = d.keys()
    df = pd.concat([df, temp] , axis = 1)
    df = df.set_index('AP')

    RP_LIST = sorted(list(set([x[:find_nth(x, '.', 2)] for x in list(df.columns)])))
    RP_MAP = {key : i for i, key in enumerate(RP_LIST)}
    INV_RP_MAP = {i : key for i, key in enumerate(RP_LIST)}
    TIMESTEPS = 5

    radio_map = {}
    for direction in DIRECTIONS:
        arr = np.ndarray((len(AP_LIST), len(RP_MAP), TIMESTEPS), dtype = np.float16)
        for key in RP_MAP:
            print(key + '.' + direction)
            cols = [x for x in df.columns if key + '.' + direction in x]
            if len(cols) == 0:
                temp = np.full((len(AP_LIST) , TIMESTEPS) , fill_value=np.nan, dtype=np.float16)
            elif 0 < len(cols) < TIMESTEPS:
                print(df[cols].to_numpy().shape, np.full((len(AP_LIST) , TIMESTEPS - len(cols)) , fill_value=np.nan, dtype=np.float16).shape)
                temp = np.concatenate((df[cols].to_numpy() , np.full((len(AP_LIST) , TIMESTEPS - len(cols)) , fill_value=np.nan, dtype=np.float16)), axis = 1)
            else:
                temp = df[cols].to_numpy()
            arr[:,RP_MAP[key],:] = temp 

        radio_map[direction] = arr
    
    I = {}
    for direction in DIRECTIONS:
        T = (radio_map[direction] > GAMMA).astype(int).sum(axis = 2)
        _I = (T > M).astype(int)
        I[direction] = _I

    S = {}
    for direction in DIRECTIONS:
        _S = np.ndarray((len(RP_MAP) , len(RP_MAP)))
        _I = I[direction]
        for i in range(len(RP_MAP)):
            for j in range(len(RP_MAP)):
                _S[i][j] = hamming(_I[:, i] , _I[:, j])
        S[direction] = _S


    delta = {}
    psi = {}
    for direction in DIRECTIONS:
        _psi = np.sum(radio_map[direction], axis = 2) / TIMESTEPS
        psi[direction] = _psi
        # print(_psi.shape)
        _delta = np.sum((radio_map[direction] - _psi[:, :, np.newaxis]) ** 2 , axis = 2) / (TIMESTEPS-1)
        _delta = np.sum(np.nan_to_num(_delta) * I[direction] , axis = 0) * (1 / (np.sum(I[direction] , axis = 0)))
        # print(_delta)
        delta[direction] = _delta

    

    CH = collections.defaultdict(lambda : collections.defaultdict(set))
    FL = collections.defaultdict(lambda : collections.defaultdict(set))
    for direction in DIRECTIONS:
        B = set([i for i in range(len(RP_MAP))])
        Bprime = set([i for i in range(len(RP_MAP))])
        edgeset = set()
        visited = set()
        _S = S[direction]
        k = -1
        while B:
            k += 1
            fl = set()
            node = B.pop()
            for j in Bprime:
                if j != node and _S[j,node] >= ETA:
                    fl.add(j)
                    if j not in visited:
                        visited.add(j)
                    else:
                        edgeset.add(j)
            B = B - fl
            CH[direction][k] = set([node])
            FL[direction][k] = fl

        K = k
        for k in range(K+1):
            temp = (CH[direction][k] | FL[direction][k])
            cluster = list(temp - edgeset)
            stabilities = delta[direction][cluster]
            CH[direction][k] = set([cluster[np.argmin(stabilities)]])
            FL[direction][k] = temp - CH[direction][k]

    
    clusters = {}
    for temp_dir in DIRECTIONS:
        temp = {}
        for key in range(len(CH[temp_dir])):
            temp[INV_RP_MAP[list(CH[temp_dir][key])[0]]] = set([INV_RP_MAP[x] for x in FL[temp_dir][key]])
        clusters[temp_dir] = temp

    return clusters


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
