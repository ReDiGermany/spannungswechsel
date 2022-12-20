import sys
import json

sys.path.append("../../car")
from round_item import round_group

def direct_neighbour(a,to):
    return a

if __name__ == "__main__":
    cones = {
        "blue":[
            {"x":45,"z":81},
            {"x":286,"z":235},
            {"x":246,"z":180},
            {"x":194,"z":138},
            {"x":297,"z":239},
            {"x":285,"z":290},
            {"x":183,"z":431},
            {"x":243,"z":212},
        ],
        "red":[
            {"x":-25,"z":80},
            {"x":-23,"z":130},
            {"x":7,"z":163},
            {"x":50,"z":191},
            {"x":102,"z":196},
            {"x":161,"z":204},
            {"x":203,"z":226},
            {"x":169,"z":367}
        ]
    }
    my_dict = {
        "blue":{},
        "red":{},
    }
    blocker = {}
    for color in cones:
        for item in cones[color]:
            temp = round_group(item)
            my_dict[color][temp["center"]]=item
            my_dict[color][temp["center"]]["grid_position"] = temp["center_raw"]
            for b in temp["corners"]:
                blocker[b] = item
    a = direct_neighbour(my_dict["blue"],{"x":0,"y":0})
    print(json.dumps(a))