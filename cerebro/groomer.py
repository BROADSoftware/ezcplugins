
from misc import ERROR,lookupRepository,setDefaultInMap


def groom(plugin, model):
    setDefaultInMap(model["cluster"]["cerebro"], "disabled", False)
    if model["cluster"]["cerebro"]["disabled"]:
        return False
    else:
        lookupRepository(model, "cerebro")
        return True
    
