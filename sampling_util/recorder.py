import subprocess
import json
import time

CMD = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
ROUTE_MODE = False
devName = "mba"
DUP = 5
direction = ["North", "East", "South", "West"]

def get_fp_triad_list():
    scan_cmd = subprocess.Popen(['sudo', CMD, '-s'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    scan_out, scan_err = scan_cmd.communicate()
    scan_out_lines = str(scan_out).split("\\n")[1:-1]
    triad_list = []
    for l in scan_out_lines:
        print(l)
        indexOfFirstComma = l.find(":")
        indexOfMAC = indexOfFirstComma - 2
        name = l[:indexOfMAC - 1].strip()
        mac = l[indexOfMAC: indexOfMAC + 17]
        rssi = int(l[indexOfMAC + 18:indexOfMAC + 22])
        triad_list.append([name, mac, rssi])
    triad_list.sort(key = lambda x: x[0])
    return triad_list

def json_package(locId, d):
    """
        file name: sectionId_devName.json 
        NOTICE: It should be a JSON LIST but for the convenience of incremental record, brackets are eliminated.
        {
            "location" : string,
            "timestamp" : timestamp,
            "counter" : integer,
            "fingerprint" : [[Triad], [Triad], ... , [Triad]],
        } * N lines
    """
    fail_counter = 5
    while fail_counter > 0:
        readingAP = get_fp_triad_list()
        if len(readingAP) > 0:
            break
        fail_counter -= 1
    one_record = {
        "location" : locId,
        "direction" : d,
        "timestamp" : int(time.time()),
        "counter" : len(readingAP),
        "fingerprint" : readingAP
    }
    return json.dumps(one_record)

def main():
    secId = input("which room you are at : ").replace(" ", "")
    fileName = devName + "_" + str(secId) + ".json"
    locId = input("what is your current location : ")
    while locId:
        print("[normal mode] start collecting sample#{}.".format(locId))
        with open(fileName, "a+") as f:
            for d in direction:
                _ = input(f"Please Face {d}! Press Enter To Continue")
                if DUP > 0:
                    for i in range(DUP):
                        f.write(json_package(str(locId), d) + "\n")
                else:
                    f.write(json_package(str(locId), d) + "\n")
        print("[normal mode] sample#{} collected.".format(locId))
        locId = input("what is your current location : ")

def route_mode():
    devName = input("what is your device : ").replace(" ", "")
    secId = input("which section you are at : ").replace(" ", "")
    fileName = devName + "_" + str(secId) + ".json"
    interval = int(input("route mode interval (s) : "))
    totalCtr = int(input("total samples to gather : "))
    for locId in range(totalCtr):
        print("[route mode] start collecting sample#{}.".format(locId))
        with open(fileName, "a+") as f:
            for d in direction:
                _ = input(f"Please Face {d}! Press Enter To Continue")
                if DUP > 0:
                    for i in range(DUP):
                        f.write(json_package(str(locId), d) + "\n")
                else:
                    f.write(json_package(str(locId), d) + "\n")
        print("[route mode] sample#{} has been collected, go to the next spot with in {} seconds.".format(locId, interval))
        time.sleep(interval)

if ROUTE_MODE:
    route_mode()
else:
    main()