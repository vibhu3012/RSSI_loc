def gen_filter(rssi:list, rps:dict, alg:str) -> list:
    filter = [r!= None for r in rssi]
    return filter   # naive rssi based ap filter

def apply_filter(rssi, filter:list): 
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
            apply_filter(rssi[k])
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