
from misc import ERROR,lookupRepository,setDefaultInMap


def groom(plugin, model):
    setDefaultInMap(model["cluster"]["cerebro"], "disabled", False)
    if not model["cluster"]["cerebro"]["disabled"]:
        lookupRepository(model, "cerebro")
