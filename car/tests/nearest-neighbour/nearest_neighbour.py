import math
import json

# Calculate distance between 2 points
# sqrt( (x1-x2)^2 + (y1-y2)^2 )
def distance_of(el1,el2):
    return math.sqrt(math.pow(el1["x"]-el2["x"],2) + math.pow(el1["y"]-el2["y"],2))

# Basic Template (to save some readability)
def template(item,distance,same_color):
    return {
        "distance": distance,
        "id": item["id"],
        "x": item["x"],
        "y": item["y"],
        "color": item["color"],
        "sameColor": same_color
    }

# Sorter function to sort by distance between points
def sort_by_distance(item):
    return item.get("distance")

def parse(pts, cache, l, tension, numOfSeg, res, rPos):
    i = 2
    while i < l:

        pt1 = pts[i]
        pt2 = pts[i+1]
        pt3 = pts[i+2]
        pt4 = pts[i+3]

        t1x = (pt3 - pts[i-2]) * tension
        t1y = (pt4 - pts[i-1]) * tension
        t2x = (pts[i+4] - pt1) * tension
        t2y = (pts[i+5] - pt2) * tension

        t = 0
        while t < numOfSeg:

            c = t << 2 #t * 4;
            c1 = cache[c]
            c2 = cache[c+1]
            c3 = cache[c+2]
            c4 = cache[c+3]
            
            res[rPos] = c1 * pt1 + c2 * pt3 + c3 * t1x + c4 * t2x
            rPos = rPos + 1
            res[rPos] = c1 * pt2 + c2 * pt4 + c3 * t1y + c4 * t2y
            rPos = rPos + 1
            t = t + 1
        i = i + 2

# https://github.com/gdenisov/cardinal-spline-js/blob/master/src/curve_calc.js
def get_curve_points(points, tension = 0.5, numOfSeg = 3, close = False):
    i = 1
    l = len(points)
    rPos = 0
    rLen = (l-2) * numOfSeg + 2 + (2 * numOfSeg if close else 0)
    res = [0.0] * rLen
    cache = [0.0] * ((numOfSeg + 2) * 4)
    cachePtr = 4

    pts = points #js> pts = points.slice(0);
    
    if close:
        pts.insert(0,points[l - 1])				    # insert end point as first point
        pts.insert(0,points[l - 2])
        pts.append(points[0]) 		                # first point as last point
        pts.append(points[1]) 		                # first point as last point
    else:
        pts.insert(0,points[1])					    # copy 1. point and insert at beginning
        pts.insert(0,points[1])
        pts.append(points[l])	                    # duplicate end-points
        pts.append(points[l+1])	                    # duplicate end-points

    # cache inner-loop calculations as they are based on t alone
    cache[0] = 1								# 1,0,0,0

    i=0
    while i < numOfSeg:
        st = i / numOfSeg
        st2 = st * st
        st3 = st2 * st
        st23 = st3 * 2
        st32 = st2 * 3

        cache[cachePtr] =	st23 - st32 + 1;	# c1
        cachePtr = cachePtr + 1
        cache[cachePtr] =	st32 - st23;		# c2
        cachePtr = cachePtr + 1
        cache[cachePtr] =	st3 - 2 * st2 + st;	# c3
        cachePtr = cachePtr + 1
        cache[cachePtr] =	st3 - st2;			# c4
        cachePtr = cachePtr + 1
        i = i+1

    cachePtr = cachePtr + 1
    cache[cachePtr] = 1;						# 0,1,0,0

    # calc. points
    parse(pts, cache, l, tension, numOfSeg, res, rPos)

    if (close):
        #l = points.length;
        pts = []
        pts.push(points[l - 4], points[l - 3], points[l - 2], points[l - 1]) # second last and last
        pts.push(points[0], points[1], points[2], points[3]) # first and second
        parse(pts, cache, 4, tension, numOfSeg, res, rPos)

    # add last point
    l = 0 if close else len(points) - 2
    res[rPos] = points[l]
    rPos = rPos + 1
    res[rPos] = points[l+1]

    for idx,item in enumerate(res):
        res[idx] = round(item,2)

    # TODO: Check why this shit is necessary
    # otherwhise the last point would either be missing or some weird shit would happen (try removing the [2:-2:])
    re = res[2:-2:]
    re.append(points[len(points)-2])
    re.append(points[len(points)-1])

    return re

def check_permut(item1,item2,item3,temp_dict,neighbours,idx):
    key = "{}={}={}".format(item1,item2,item3)
    neighbours[idx]["visible"] = True
    if key in temp_dict.keys():
        neighbours[idx]["visible"] = False
        temp_dict[key] = True
        return key,True
    temp_dict[key] = True
    return key,False

# Main Function
def nearest_neighbour(neighbours,detailed = False):
    route = {}

    # Finding outlines
    pylons = {
        "blue":[],
        "red":[]
    }
    for item in neighbours:
        # print(item)
        pylons[item["color"]].append({
            'id': item['id'],
            'color': item['color'],
            'x': item['x'],
            'y': item['y'],
            'distance': 0.0
        })
    for color in pylons:
        for idx,item in enumerate(pylons[color]):
            if idx > 0:
                dist = distance_of(item,pylons[color][0])
                item["distance"] = dist
        pylons[color].sort(key=sort_by_distance)

    # Finding nearest neighbours (1x same color, 1x different color) and adding
    # it as "neighbour_same_color" & "neighbour_other_color" to the object
    for idx,item in enumerate(neighbours):
        nearest_same_color = template(item, 999999999999, True)
        nearest_other_color = template(item, 999999999999, False)
        # item["neighbours"] = []

        for idx1,item1 in enumerate(neighbours):
            if idx != idx1:
                dist = distance_of(item,item1)
                temp_item = template(item1,dist, item1["color"] == item["color"] )
                # item["neighbours"].append(temp_item)
                if temp_item["color"] == item["color"]:
                    if nearest_same_color["distance"] > temp_item["distance"]:
                        nearest_same_color = temp_item
                else:
                    if nearest_other_color["distance"] > temp_item["distance"]:
                        nearest_other_color = temp_item 

        item["neighbour_same_color"] =  nearest_same_color
        item["neighbour_other_color"] =  nearest_other_color

    # Building Base route
    for idx,item in enumerate(neighbours):
        other = item["neighbour_other_color"]
        same = item["neighbour_same_color"]
        i = str(idx)
        mid = {
            "x": ( item["x"] + other["x"] ) / 2,
            "y": ( item["y"] + other["y"] ) / 2,
            "id": i
        }
        route[i] = mid
    

    # Getting next Points sorted by distance 
    for item in route:
        route[item]["next"] = []
        for item1 in route:
            if item != item1:
                distance = distance_of(route[item],route[item1])
                if distance > 0.0:
                    route[item]["next"].append({
                        "x": route[item1]["x"],
                        "y": route[item1]["y"],
                        "id": route[item1]["id"],
                        "distance": distance
                    })
        route[item]["next"].sort(key=sort_by_distance)

    return_route = route["0"]

    # Removing double entries
    temp_dict = {}
    for idx,item in enumerate(return_route["next"]):
        key = "{}-{}".format(item["x"],item["y"])
        if key in temp_dict.keys():
            return_route["next"].pop(idx)
        temp_dict[key] = True

    curved_points = []
    blue_curved = []
    red_curved = []

    # Preparing points array & calculating curves
    if detailed:
        givenPoints = [return_route["x"],return_route["y"]]
        for item in return_route["next"]:
            givenPoints.append(item["x"])
            givenPoints.append(item["y"])
        curve = get_curve_points(givenPoints)
        curved_points = {"x":curve[::2],"y":curve[1::2]}

    # Preparing points array & calculating curves
    if detailed:
        givenPoints = []
        for item in pylons["blue"]:
            givenPoints.append(item["x"])
            givenPoints.append(item["y"])
        curve = get_curve_points(givenPoints)
        blue_curved = {"x":curve[::2],"y":curve[1::2]}

    # Preparing points array & calculating curves
    if detailed:
        givenPoints = []
        for item in pylons["red"]:
            givenPoints.append(item["x"])
            givenPoints.append(item["y"])
        curve = get_curve_points(givenPoints)
        red_curved = {"x":curve[::2],"y":curve[1::2]}

    return return_route,neighbours,curved_points,pylons,blue_curved,red_curved