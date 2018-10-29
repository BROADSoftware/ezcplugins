

from misc import ERROR,setDefaultInMap,lookupRepository

def groom(plugin, model):
    setDefaultInMap(model["cluster"]["docker"], "disabled", False)
    if not model["cluster"]["docker"]["disabled"]:
        lookupRepository(model, "docker")
    
