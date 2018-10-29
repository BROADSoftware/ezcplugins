

from misc import ERROR,setDefaultInMap,lookupRepository

def groom(plugin, model):
    setDefaultInMap(model["cluster"]["docker"], "disabled", False)
    if model["cluster"]["docker"]["disabled"]:
        return False
    else:
        lookupRepository(model, "docker")
        return True
    
