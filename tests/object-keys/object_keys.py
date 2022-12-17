import random
import sys

sys.path.insert(0, '../../car/')
from round_item import round_item

def r(x=-50,y=50):
    return random.randint(x,y)

if __name__ == "__main__":
    temp_dict = {}
    i=0
    while i < 10_000:
        key = round_item({"x":r(),"y":r()})
        if key not in temp_dict:
            temp_dict[key] = True
            # print(f"Added {key}")
        # else:
            # print(f"Found double {key}")
        i = i+1
    # print(temp_dict)