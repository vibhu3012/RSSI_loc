from rssicore import *
import subprocess, random, pickle

CMD = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"

def sampler(platform:str, file=None):
    if platform == "macos":
        return macSampler()
    if platform == "simulation":
        return fileSampler(file)
    raise ValueError

def macSampler():
    scan_cmd = subprocess.Popen(['sudo', CMD, '-s'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print("cmd line above")
    scan_out, scan_err = scan_cmd.communicate()
    scan_out_lines = str(scan_out).split("\\n")[1:-1]
    raw = {}
    for l in scan_out_lines:
        indexOfFirstComma = l.find(":")
        indexOfMAC = indexOfFirstComma - 2
        name = l[:indexOfMAC - 1].strip()
        mac = l[indexOfMAC: indexOfMAC + 17]
        rssi = int(l[indexOfMAC + 18:indexOfMAC + 22])
        raw[mac] = rssi
    return raw

def fileSampler(file:str):
    # when sample from raw file directly
    # with open(file, "rb") as f:
    #     raws = f.readlines()
    #     random.seed()
    #     oneline = json.loads(random.choice(raws))
    # fp = oneline["fingerprint"]
    # ret = {}
    # for r in fp:
    #     ret[r[1]] = r[2]
    # id = ".".join([file.replace(".json", ""), oneline["location"], oneline["direction"].lower(), str(oneline["timestamp"])])
    with open(file, "rb") as f:
        test_dict = pickle.load(f)
    
    random.seed()
    key = random.choice(list(test_dict.keys()))
    # return test_dict[key], ".".join(key.split(".")[:-1])
    return test_dict[key], key