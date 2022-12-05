#!/usr/bin/env python3.8
import json

from nearest_neighbour import nearest_neighbour

neighbours = [
    { "id":"1","color": "blue", "x": 32, "y": 59},
    { "id":"2","color": "blue", "x": -8, "y": 155},
    { "id":"3","color": "blue", "x": -56, "y": 176},
    { "id":"4","color": "blue", "x": 23, "y": 111},
    { "id":"5","color": "red", "x": -32, "y": 51},
    { "id":"6","color": "red", "x": -57, "y": 94},
    # { "id":"7","color": "yellow", "x": -99, "y": 176},
]

route,neighbours,curve,pylons,blue_curved,red_curved = nearest_neighbour(neighbours,True)

print(json.dumps({
    "neighbours":neighbours,
    "route":route,
    "curve":curve,
    "pylons":pylons,
    "blueCurved":blue_curved,
    "redCurved":red_curved,
}))
# print(json.dumps({"neighbours":neighbours,"route":route,"curve":curve}, indent=2))
# print(json.dumps(route, indent=2))
# print(json.dumps({"neighbours":neighbours,"route":route["0"]}))