def genFilter(rssi:list, rps:dict, alg:str) -> list:
    if alg == "naive":
        return naiveAPFilter(rssi)
    raise ValueError


def naiveAPFilter(rssi:list):
    '''
    naive rssi based ap filter
    '''
    return [r!= None for r in rssi]

def applyFilter(rssi, filter:list): 
    # onsite change
    if type(rssi) == list:
        ret = []
        for (r, useAP) in zip(rssi, filter):
            if useAP:
                ret.append(r)
        rssi = ret
        return
    if type(rssi) == dict:
        for k in rssi.keys():
            applyFilter(rssi[k], filter)
        return
    raise TypeError

def aligner(rssi_reading:dict, ap_list:list) -> list:
    ret = []
    for ap in ap_list:
        if ap in rssi_reading.keys():
            ret.append(rssi_reading[ap])
        else:
            ret.append(None)
    return ret