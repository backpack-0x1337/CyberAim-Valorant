

def get_center_cord(p1, p2):
    return float((p1 + p2) / 2)


def get_list_by_classname(ent_list, classname):
    newList = []
    for item in ent_list:
        if item["name"] == classname:
            newList.append(item)
    return newList


