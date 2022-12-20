def round_by_base(x,base=5):
    return base * round(x/base)

def round_coordinates(x,y,base=5):
    return f'{round_by_base(x,base)}:{round_by_base(y,base)}'

def round_item(item,base=5):
    return round_coordinates(item["x"],item["z"],base)

def round_group(item,base=5):
    rawx = round_by_base(item["x"],base)
    rawy = round_by_base(item["z"],base)

    return {
        "center": f"{rawx}:{rawy}",
        "center_raw":{"x":rawx,"y":rawy},
        "corners": [
            f"{rawx-base}:{rawy-base}", f"{rawx}:{rawy-base}", f"{rawx+base}:{rawy-base}",
            f"{rawx-base}:{rawy}", f"{rawx+base}:{rawy}", # f"{rawx}:{rawy}", @ middle but no need to block that due to it wont count up then
            f"{rawx-base}:{rawy+base}", f"{rawx}:{rawy+base}", f"{rawx+base}:{rawy+base}",
        ]
    }
