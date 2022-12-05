#!/usr/bin/python3.8
import subprocess
import json
import re

def shell(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    except  e:
        output = str(e.output)
    finished = output.decode("utf-8").split('\n')
    return finished

def get_wifi():
    networks = shell('iwconfig')

    wlan0 = {
        "ssid": "",
        "nickname": "",
        "frequency": "",
        "access_point": "",
        "bit_rate": "",
        "link_quality": "",
        "signal_level": "",
        "noise_level": "",
    }

    found = False
    for line in networks:
        if line.startswith("wlan0"):
            found = True
            wlan0["ssid"] = re.findall("SSID:\"([^\"]*)\"",line)[0]
            wlan0["nickname"] = re.findall("Nickname:\"([^\"]*)\"",line)[0]
        elif found:

            frequency = re.findall("Frequency:([^ ]*) GHz",line)
            if(frequency):
                wlan0["frequency"] = "{} GHz".format(frequency[0])
            
            access_point = re.findall("Access Point: ([^ ]*) ",line)
            if(access_point):
                wlan0["access_point"] = access_point[0]
            
            bit_rate = re.findall("Bit Rate:([^ ]*) Mb/s",line)
            if(bit_rate):
                wlan0["bit_rate"] = "{} Mb/s".format(bit_rate[0])
            
            link_quality = re.findall("Link Quality=([^ ]*) ",line)
            if(link_quality):
                wlan0["link_quality"] = "{}".format(link_quality[0])
            
            signal_level = re.findall("Signal level=([^ ]*) ",line)
            if(signal_level):
                wlan0["signal_level"] = "{}".format(signal_level[0])
            
            noise_level = re.findall("Noise level=([^ ]*)",line)
            if(noise_level):
                wlan0["noise_level"] = "{}".format(noise_level[0])
            
        if line == "" and found:
            break
    return wlan0
