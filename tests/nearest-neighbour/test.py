#!/usr/bin/env python3.8
import json
import sys

sys.path.insert(0, '../../car')
from nearest_neighbour import nearest_neighbour

neighbours = [
    { "id":"1", "color": "blue", "x": 32, "y": 59},
    { "id":"2", "color": "blue", "x": -8, "y": 155},
    { "id":"3", "color": "blue", "x": -56, "y": 176},
    { "id":"4", "color": "blue", "x": 23, "y": 111},
    { "id":"5", "color": "red", "x": -32, "y": 51},
    { "id":"6", "color": "red", "x": -57, "y": 94},
    # { "id":"7","color": "yellow", "x": -99, "y": 176},
]
neighbours = [
    {"x": 28.173599243164062, "y": -4.217029094696045, "color": "blue", "id": "1"},
    {"x": 18.451313018798828, "y": -0.16856080293655396, "color": "blue", "id": "2"},
    {"x": 69.88467407226562, "y": -25.95035171508789, "color": "blue", "id": "4"},
    {"x": 71.71773529052734, "y": -26.670181274414062, "color": "blue", "id": "6"},
    {"x": 32.09401321411133, "y": -15.31482219696045, "color": "blue", "id": "5"},
    {"x": 32.34636688232422, "y": -15.284357070922852, "color": "blue", "id": "15"},
    {"x": -26.044931411743164, "y": -9.867493629455566, "color": "red", "id": "0"},
    {"x": -30.572906494140625, "y": -0.9726141095161438, "color": "red", "id": "3"},
    {"x": -30.52215576171875, "y": -0.8885288834571838, "color": "red", "id": "7"},
    {"x": -38.667171478271484, "y": -7.109703063964844, "color": "red", "id": "8"},
    {"x": -30.377460479736328, "y": -0.8516703844070435, "color": "red", "id": "9"}
]

route,neighbours,curve,pylons,blue_curved,red_curved = nearest_neighbour(neighbours,False)

data = json.dumps({
    "neighbours":neighbours,
    "route":route,
    "curve":curve,
    "pylons":pylons,
    "blueCurved":blue_curved,
    "redCurved":red_curved,
})

print(data)
f = open("../../dashboard/json/nearest-neighbour.json", "w")
f.write(data)
f.close()
# print(json.dumps({"neighbours":neighbours,"route":route,"curve":curve}, indent=2))
# print(json.dumps(route, indent=2))
# print(json.dumps({"neighbours":neighbours,"route":route["0"]}))