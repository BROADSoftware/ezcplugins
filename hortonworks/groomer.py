
import os
from misc import ERROR, setDefaultInMap, appendPath

def groom(plugin, model):
    setDefaultInMap(model["cluster"]["hortonworks"], "disabled", False)
    version = model["cluster"]["hortonworks"]["version"]
    l = filter(lambda x: x["version"] == version, model["config"]["repositories"]["hortonworks"])
    if len(l) > 1:
        ERROR("Hortonworks version '{}' is defined twice in configuration file!".format(version))
    if len(l) != 1:
        ERROR("Hortonworks version '{}' is not defined in configuration file!".format(version))
    model["data"]["hortonworks"] = l[0]
    
    ansible_repo_folder = appendPath(os.path.dirname(model["data"]["configFile"]),  model["config"]["hortonworks"]["ansible_repo_folder"]) 
    model["config"]["hortonworks"]["ansible_repo_folder"] = ansible_repo_folder
    model["data"]["rolePaths"].add(appendPath(ansible_repo_folder, "roles"))
