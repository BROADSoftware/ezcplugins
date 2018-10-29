
from misc import setDefaultInMap


def groom(plugin, model):
    if "ansible" in model["cluster"]:
        setDefaultInMap(model["cluster"]["ansible"], "disabled", False)
        return not model["cluster"]["ansible"]["disabled"]
    else:
        return False
