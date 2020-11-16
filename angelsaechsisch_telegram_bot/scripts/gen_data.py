import os
import json

root_path = os.getcwd()
data_path = "/angelsaechsisch_telegram_bot/data"
en_path = "/words.txt"
de_path = "/de.txt"
out_path = "/data.json"

with open(root_path + data_path + en_path, "r") as f:
    en_raw = f.read()

with open(root_path + data_path + de_path, "r") as f:
    de_raw = f.read()

en_raw = en_raw.split("\n")
de_raw = de_raw.split("\n")

en = set(en_raw)
de = set(de_raw)

en_clean = en - de

en_final = {i.lower() for i in en_clean}
en_final = list(en_final)
en_final.sort()

with open(root_path + data_path + out_path, "w") as f:
    json.dump(en_final,f)