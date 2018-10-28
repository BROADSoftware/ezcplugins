
from misc import ERROR,lookupRepository,setDefaultInMap


def groom(plugin, model):
    setDefaultInMap(model["cluster"]["jdk_oracle"], "disabled", False)
    if not model["cluster"]["jdk_oracle"]["disabled"]:
        lookupRepository(model, "jdk_oracle")
