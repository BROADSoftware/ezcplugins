

from misc import ERROR,setDefaultInMap

def groom(plugin, model):
    setDefaultInMap(model["cluster"]["docker"], "disabled", False)
    version = model["cluster"]["docker"]["version"]
    l = filter(lambda x: x["version"] == version, model["config"]["repositories"]["docker"])
    if len(l) > 1:
        ERROR("Docker version '{}' is defined twice in configuration file!".format(version))
    if len(l) != 1:
        ERROR("Docker version '{}' is not defined in configuration file!".format(version))
    model["data"]["docker"] = l[0]
    
