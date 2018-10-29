
from misc import ERROR,lookupRepository,setDefaultInMap


def groom(plugin, model):
    setDefaultInMap(model["cluster"]["jdk_oracle"], "disabled", False)
    if model["cluster"]["jdk_oracle"]["disabled"]:
        return False
    else:
        lookupRepository(model, "jdk_oracle")
        return True
