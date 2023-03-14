import subprocess

CMD = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"

def sampler(platform:str)->dict:
    if platform == "macos":
        return macSampler
    raise ValueError

def macSampler():
    scan_cmd = subprocess.Popen(['sudo', CMD, '-s'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    scan_out, scan_err = scan_cmd.communicate()
    scan_out_lines = str(scan_out).split("\\n")[1:-1]
    triad_list = {}
    for l in scan_out_lines:
        print(l)
        indexOfFirstComma = l.find(":")
        indexOfMAC = indexOfFirstComma - 2
        name = l[:indexOfMAC - 1].strip()
        mac = l[indexOfMAC: indexOfMAC + 17]
        rssi = int(l[indexOfMAC + 18:indexOfMAC + 22])
        triad_list[mac] = rssi
    return triad_list