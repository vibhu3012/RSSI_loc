import json
import seaborn as sns
import matplotlib.pyplot as plt

fileName = "./datasets/mac_pro_m1pro_C.json"

all = []
with open(fileName, "r") as f:
    sample = f.readlines()

for sample_line in sample:
    record = json.loads(sample_line)
    triad_list = record["fingerprint"]
    rssis = []
    for triad in triad_list:
        rssis.append(triad[2])
    all.append(rssis)

sns.displot(all, kind = "kde")
plt.savefig("C.png")