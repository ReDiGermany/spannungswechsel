import math
import json

neighbours = [
    { "id":"1","color": "blue", "x": 32, "y": 59},
    { "id":"2","color": "blue", "x": -8, "y": 155},
    { "id":"3","color": "blue", "x": -56, "y": 176},
    { "id":"4","color": "blue", "x": 23, "y": 111},
    { "id":"5","color": "red", "x": -32, "y": 51},
    { "id":"6","color": "red", "x": -57, "y": 94},
    # { "id":"7","color": "yellow", "x": -99, "y": 176},
]

def distance_of(el1,el2):
    return math.sqrt(math.pow(el1["x"]-el2["x"],2) + math.pow(el1["y"]-el2["y"],2))

def dist_ify(item,distance,same_color):
    return { "distance": distance, "id": item["id"], "x": item["x"], "y": item["y"], "color": item["color"], "sameColor":same_color }

for idx,item in enumerate(neighbours):
    temp = []
    nearestSame = dist_ify(item, 999999999999,True)
    nearestOther = dist_ify(item, 999999999999,False)
    for idx1,item1 in enumerate(neighbours):
        if idx != idx1:
            dist = distance_of(item,item1)
            n = dist_ify(item1,dist, item1["color"] == item["color"] )
            if n["color"] == item["color"]:
                if nearestSame["distance"] > n["distance"]:
                   nearestSame = n
            else:
                if nearestOther["distance"] > n["distance"]:
                   nearestOther = n 

    item["neighbours"] = [nearestOther,nearestSame]

route = {}

for idx,item in enumerate(neighbours):
    for idx1,item1 in enumerate(item["neighbours"]):
        if not item1["sameColor"]:
            mid = {
                "x": ( item["x"] + item1["x"] ) / 2,
                "y": ( item["y"] + item1["y"] ) / 2,
                "id": str(idx)
            }
            # item["mid"] = mid
            route[str(idx)] = mid

def sort_by_distance(item):
    return item.get("distance")

for item in route:
    route[item]["next"] = []
    for item1 in route:
        if item != item1:
            distance = distance_of(route[item],route[item1])
            if distance > 0.0:
                route[item]["next"].append({"x":route[item1]["x"],"y":route[item1]["y"],"id":route[item1]["id"],"distance":distance})
    route[item]["next"].sort(key=sort_by_distance)

# print(json.dumps({"neighbours":neighbours,"route":route}, indent=2))
print(json.dumps({"neighbours":neighbours,"route":route["0"]}))