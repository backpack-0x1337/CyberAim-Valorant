

def get_center_cord(p1, p2):
    return float((p1 + p2) / 2)


def get_list_by_classname(list, classname):
    newList = []
    for item in list:
        if item["name"] == classname:
            newList.append(item)
    return newList


