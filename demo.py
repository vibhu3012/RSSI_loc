import sys, json, pickle, time
from threading import Thread, Lock

from rssicore.RPcluster import cluster, neighbors
from rssicore.APselector import selector, aligner, gen_filter
from rssicore.Sampler import sampler
from rssicore.Discrete import estimator, est2loc

if len(sys.argv) < 2:
    print("plz specify config file")

with open(sys.argv[1], "r") as cf:
    conf = json.load(cf)

# with open(conf["SRC_PATH"] + conf["RP_LOCATION"], "r") as lf:
#     loc = json.load(lf)

with open(conf["SRC_PATH"] + conf["RP_META"], "r") as mf:
    meta = json.load(mf)
    all_ap = meta["ap_list"]

with open(conf["SRC_PATH"] + conf["RP_PKL"], "rb") as rpf:
    all_rps = pickle.load(rpf) # rp_db is too large hence should use pickle instead of json

try:
    with open(conf["SRC_PATH"] + conf["PRE_CLUSTERED"], "r") as clf:
        c_json = json.load(clf)
        c_label = c_json["label"] # label is a long list of cluster id
        c_enumerate = c_json["enumerate"] # list is a dict of members of each cluster
        c_head = c_json["head"] # head is a dict of head index of each cluster
except FileNotFoundError:
    c_label, c_enumerate, c_head = cluster(all_rps, alg=conf["RP_CLUSTER_ALG"])
    c_json = {
        "label" : c_label,
        "enumerate" : c_enumerate,
        "head" : c_head,
    }
    with open(conf["SRC_PATH"] + conf["PRE_CLUSTERED"], "w+") as clf:
        json.dump(c_json, clf)

rssi_buf = None
timestamp = None

def rssi_sampler():
    global rssi_buf
    global timestamp
    while True:
        cur_rssi = sampler(conf["PLATFORM"])
        if len(cur_rssi) > 0:
            rssi_buf = cur_rssi
            timestamp = time.localtime()
        time.sleep(conf["SAMPLE_INTERVAL"])

sample_thread = Thread(target=rssi_sampler, daemon=True)
sample_thread.start()

# pipeline starts here ===================================
while True:
    if not rssi_buf:
        time.sleep(conf["LOC_INTERVAL"])
        continue

    # rssi in the format of meta.json
    rssi = aligner(rssi_buf, all_ap)

    # subset of all_rps
    roi_rps = neighbors(rssi=rssi, 
                        all=all_rps,
                        heads=c_head,
                        enum=c_enumerate)

    # binary filter
    ap_filter = selector(rssi=rssi,
                        roi=roi_rps,
                        alg=conf["AP_SELECT_ALG"])

    # shrank the aps
    rssi = gen_filter(rssi, ap_filter)
    roi_rps = gen_filter(roi_rps, ap_filter)

    # localization job
    estimation = estimator(rssi=rssi, ref=roi_rps, alg=conf["DISCRETE_ALG"])
    # location = est2loc(est=estimation, loc_ref=loc)
    location = est2loc(est=estimation, loc_ref=roi_rps)
    print("[{}] current location is {}".format(time.strftime("%H:%M:%S", timestamp), location))

# eof pipeline ===========================================