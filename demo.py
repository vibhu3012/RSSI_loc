import sys, json, pickle, time
from threading import Thread, Lock

from rssicore import * # logging
from rssicore.RPcluster import cluster, coarseLoc
from rssicore.APselector import genFilter, aligner, applyFilter
from rssicore.Sampler import sampler
from rssicore.Estimate import estimator, est2loc

if len(sys.argv) < 2:
    print("plz specify config file")

with open(sys.argv[1], "r") as cf:
    conf = json.load(cf)

# with open(conf["SRC_PATH"] + conf["RP_LOCATION"], "r") as lf:
#     loc = json.load(lf)
# TODO match with physical coordination

with open(conf["SRC_PATH"] + conf["RP_META"], "r") as mf:
    meta = json.load(mf)
    all_ap = meta["ap_list"]

with open(conf["SRC_PATH"] + conf["RP_PKL"], "rb") as rpf:
    all_rps = pickle.load(rpf) # rp_db is too large hence should use pickle instead of json

try:
    with open(conf["SRC_PATH"] + conf["PRE_CLUSTERED"], "r") as clf:
        clustering = json.load(clf)
except FileNotFoundError:
    clustering = cluster(all_rps, alg=conf["RP_CLUSTER_ALG"])
    with open(conf["SRC_PATH"] + conf["PRE_CLUSTERED"], "w+") as clf:
        json.dump(clustering, clf)

rssi_buf = None
timestamp = None

def rssi_sampler():
    global rssi_buf
    global timestamp
    while True:
        cur_rssi = sampler(conf["PLATFORM"], "raw_data/2023_1/Intel_3165_C5.json")
        if len(cur_rssi) > 0:
            rssi_buf = cur_rssi
            timestamp = time.localtime()
        time.sleep(conf["SAMPLE_INTERVAL"])

sample_thread = Thread(target=rssi_sampler, daemon=True)
sample_thread.start()

# pipeline starts here ===================================
while True:
    if not rssi_buf:
        warning("empty rssi fetched")
        time.sleep(conf["LOC_INTERVAL"])
        continue

    # rssi in the format of meta.json
    info("fetched rssi: " + str(rssi_buf))
    rssi = aligner(rssi_buf, all_ap)

    # subset of all_rps
    roi_rps = coarseLoc(rssi=rssi, 
                        rps=all_rps,
                        clustering=clustering)

    # binary filter
    ap_filter = genFilter(rssi=rssi,
                        rps=roi_rps,
                        alg=conf["AP_SELECT_ALG"])

    # shrank the aps
    applyFilter(rssi, ap_filter)
    applyFilter(roi_rps, ap_filter)

    # localization job
    estimation = estimator(rssi=rssi, rps=roi_rps.values(), alg=conf["DISCRETE_ALG"])
    # location = est2loc(est=estimation, loc_ref=loc)
    location = est2loc(est=estimation, loc_ref=roi_rps.keys())
    print("[{}] current location is {}".format(time.strftime("%H:%M:%S", timestamp), location))
    
    time.sleep(conf["LOC_INTERVAL"])

# eof pipeline ===========================================