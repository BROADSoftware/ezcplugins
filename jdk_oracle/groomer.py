
from misc import ERROR

def groom(plugin, model):
    version = model["cluster"]["jdk_oracle"]["version"] # Required by schema
    #print model["config"]["repositories"]["jdk_oracle"]
    l = filter(lambda x: x["version"] == version, model["config"]["repositories"]["jdk_oracle"])
    if len(l) > 1:
        ERROR("Jdk_oracle version '{}' is defined twice in configuration file!".format(version))
    if len(l) != 1:
        ERROR("Jdk_oracle version '{}' is not defined in configuration file!".format(version))
    model["data"]["jdk_oracle"] = l[0]
    

