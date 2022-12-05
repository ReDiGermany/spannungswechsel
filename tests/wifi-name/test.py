import subprocess
import json
import re


proc = subprocess.Popen('iwconfig', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
out, err = proc.communicate()
networks = out.decode("utf-8").split("\n")
wlan0 = {
    "ssid": ""
}
found = False
for line in networks:
    if line.startswith("wlan0"):
        found = True
        wlan0["ssid"] = re.findall("SSID:\"([^\"]*)\"",line)[0]
    if line == "" and found:
        break
print(json.dumps(networks,indent=4))
print(json.dumps(wlan0,indent=4))