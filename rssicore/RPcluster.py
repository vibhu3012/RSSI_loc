from rssicore.Utils import ENCODING
import numpy as np
from rssicore.Utils import find_nth, hamming
import collections

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
            cols = [x for x in df.columns if key + '.' + direction in x]
            if len(cols) == 0:
                temp = np.full((len(AP_LIST) , TIMESTEPS) , fill_value=np.nan, dtype=np.float16)
            elif 0 < len(cols) < TIMESTEPS:
                # print(df[cols].to_numpy().shape, np.full((len(AP_LIST) , TIMESTEPS - len(cols)) , fill_value=np.nan, dtype=np.float16).shape)
                temp = np.concatenate((df[cols].to_numpy() , np.full((len(AP_LIST) , TIMESTEPS - len(cols)) , fill_value=np.nan, dtype=np.float16)), axis = 1)
            else:
                temp = df[cols].to_numpy()
            arr[:,RP_MAP[key],:] = temp 

        radio_map[direction] = np.nan_to_num(arr , nan=-100.0)
    
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
                _S[i][j] = hamming(_I[:, i] , _I[:, j], LAMBDA)
        S[direction] = _S


    delta = {}
    psi = {}
    for direction in DIRECTIONS:
        _psi = np.sum(radio_map[direction], axis = 2) / TIMESTEPS
        psi[direction] = _psi
        # print(_psi.shape)
        _delta = np.sum((radio_map[direction] - _psi[:, :, np.newaxis]) ** 2 , axis = 2) / (TIMESTEPS-1)
        _delta = np.sum(_delta * I[direction] , axis = 0) * (1 / (np.sum(I[direction] , axis = 0) + LAMBDA))
        # print(_delta)
        delta[direction] = _delta

    

    CH = collections.defaultdict(lambda : collections.defaultdict(set))
    FL = collections.defaultdict(lambda : collections.defaultdict(set))

    for direction in DIRECTIONS:
        # print(direction , '##################################')
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

            # print('Candidate : ' , INV_RP_MAP[node])
            for j in Bprime:
                if j != node and _S[j,node] >= ETA:
                    fl.add(j)
                    if j not in visited:
                        visited.add(j)
                    else:
                        edgeset.add(j)
            # pprint([INV_RP_MAP[x] for x in fl])
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
    for dir in DIRECTIONS:
        temp = {}
        for k in CH[direction]:
            temp[list(CH[direction][k])[0]] = FL[direction][k]
        clusters[dir] = temp

    edgenodes = collections.defaultdict(lambda : collections.defaultdict(set))
    for dir in DIRECTIONS:
        cl = clusters[dir]
        temp = collections.defaultdict(set)
        for ch , fl in cl.items():
            for f in fl:
                temp[f].add(ch)
                if len(temp[f])>1:
                    edgenodes[dir][f] = temp[f]

        # for key in edgenodes[dir]:
        #     if len(edgenodes[dir][key]) < 2:
        #         del edgenodes[dir][key]
    
    # clusters = {}
    # for temp_dir in DIRECTIONS:
    #     temp = {}
    #     for key in range(len(CH[temp_dir])):
    #         temp[INV_RP_MAP[list(CH[temp_dir][key])[0]]] = set([INV_RP_MAP[x] for x in FL[temp_dir][key]])
    #     clusters[temp_dir] = temp

    return {'clusters' : clusters, 'sparse' : I, 'radio_map' : psi, 'inv_rp_map' : INV_RP_MAP, 'edgenodes' : edgenodes}


def monoClustering(rps) -> dict:
    '''
    cluster all into a big cluster
    '''
    member = list(rps.keys())
    head = member[0]
    return {head : member}


def coarseLoc(rssi:list, rps:dict, clustering:dict, alg:str, conf) -> dict:
    if alg == ENCODING.ALG.USEALL:
        return useall(rps)
    
    if alg == ENCODING.ALG.COARSE:
        return clusterLoc(rssi, clustering, conf)
    
    raise ValueError

def clusterLoc(rssi , clustering, conf):
    GAMMA = -80
    DIRECTIONS =  ['north', 'south', 'east', 'west']
    LAMBDA = 1 / 1000

    rssi = np.array(rssi, dtype=np.float16)
    rssi_I = (rssi > GAMMA).astype(int)

    max_sim = collections.defaultdict(set)
    select = {} # Must be of the form {RP_name : RSSI}

    for dir in DIRECTIONS:
        # maximum = -float('inf')
        clusters = clustering['clusters'][dir] #{CH : set(FLs)}
        I = clustering['sparse'][dir]
        inv_rp_map = clustering['inv_rp_map']
        radio_map = clustering['radio_map'][dir]
        edgenodes = clustering['edgenodes'][dir]

        carr = np.array(clusters.keys())
        _I = I[:, carr]
        sim = np.array([hamming(_I[:, i] , rssi_I, LAMBDA) for i in range(len(_I))])
        pos = np.argmax(sim , 0)
        max_sim[dir] = set(carr[pos]) | clusters[carr[pos]]

        # for cluster in clusters:
        #     _I = I[:, cluster]
        #     sim = hamming(_I , rssi_I)
        #     if sim > maximum:
        #         max_sim[dir] = set(cluster) | clusters[cluster]
        #         maximum = sim

        temp = max_sim[dir] & set(edgenodes.keys())
        for element in temp:
            max_sim[dir] |= clusters[element]

    for dir in DIRECTIONS:
        for element in max_sim[dir]:
            select[inv_rp_map[element]] = list(radio_map[:,element])

    return select

def useall(rps) -> dict:
    '''
    use all rps
    '''
    return rps
