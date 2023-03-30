import sys, json, pickle, time
from threading import Thread, Lock

from rssicore import * # logging
from rssicore.RPcluster import cluster, coarseLoc
from rssicore.APselector import genFilter, aligner, applyFilter
from rssicore.Sampler import sampler
from rssicore.Estimate import estimator, est2loc
from rssicore.Utils import ENCODING
from pprint import pprint

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
    clustering = cluster(all_rps, all_ap, conf)
    # with open(conf["SRC_PATH"] + conf["PRE_CLUSTERED"], "w+") as clf:
    #     json.dump(clustering, clf)

rssi_buf = None
rssi_label = None
timestamp = None

def rssi_sampler():
    global rssi_buf
    global rssi_label
    global timestamp
    while True:
        if conf["PLATFORM"] == "simulation":
            cur_rssi, label = sampler(conf["PLATFORM"], conf["SAMPLE_FILE"])
        else: 
            cur_rssi = sampler(conf["PLATFORM"])
            label = "{}".format(conf["PLATFORM"])
        if len(cur_rssi) > 0:
            rssi_buf = cur_rssi
            rssi_label = label
            timestamp = time.localtime()
        time.sleep(conf["SAMPLE_INTERVAL"])

# pprint(clustering)
# exit()

sample_thread = Thread(target=rssi_sampler, daemon=True)
sample_thread.start()

# pipeline starts here ===================================
i = 0
while i < 10:
    print('##############################################################')
    if not rssi_buf:
        warning("empty rssi fetched")
        time.sleep(conf["LOC_INTERVAL"])
        continue

    # rssi in the format of meta.json
    info("fetched label: {} @ {}".format(rssi_label, time.strftime("%H:%M:%S", timestamp)))
    if conf["PLATFORM"] != "simulation" :
        rssi = aligner(rssi_buf, all_ap)
    else:
        rssi = rssi_buf # no need to align when use simulation

    # subset of all_rps
    roi_rps = coarseLoc(rssi=rssi, 
                        rps=all_rps,
                        clustering=clustering,
                        alg=conf['COARSE_LOC_ALG'], conf = conf)
    
    info("CL done, ROI_RPS_LEN: {} @ {}".format(len(list(roi_rps.keys())), time.strftime("%H:%M:%S", timestamp)))
    
    # print(len(list(roi_rps.keys())))
    # exit()

    # binary filter
    ap_filter = genFilter(rssi=rssi,
                        rps=roi_rps,
                        alg=conf["AP_SELECT_ALG"])

    # shrank the aps
    applyFilter(rssi, ap_filter)
    applyFilter(roi_rps, ap_filter)

    def runEstimation(alg):
        # localization job
        estimation, label = estimator(rssi=rssi, rps=roi_rps, alg=alg)
        # location = est2loc(est=estimation, loc_ref=loc)
        location = est2loc(est=estimation, loc_ref=label)
        # info("location@{} is {}".format(time.strftime("%H:%M:%S", timestamp), location))
        info("predict ({}): {}".format(alg, location))
    
    if conf["DISCRETE_ALG"] == "all" :
        runEstimation(ENCODING.ALG.KNN)
        runEstimation(ENCODING.ALG.PROB)
    else:
        runEstimation(conf["DISCRETE_ALG"])

    time.sleep(conf["LOC_INTERVAL"])
    i += 1

# eof pipeline ==========================================