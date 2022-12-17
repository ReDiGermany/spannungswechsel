def round_by_base(x,base=5):
    return base * round(x/base)

def round_coordinates(x,y):
    return f'{round_by_base(x)}:{round_by_base(y)}'

def round_item(item):
    return round_coordinates(item["x"],item["y"])
