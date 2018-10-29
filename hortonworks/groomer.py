
import os
from misc import ERROR, setDefaultInMap, appendPath,lookupRepository

def groom(plugin, model):
    setDefaultInMap(model["cluster"]["hortonworks"], "disabled", False)
    if model["cluster"]["hortonworks"]["disabled"]:
        return False
    else:
        lookupRepository(model, "hortonworks") 
        if "hortonworks" not in model["config"] or "ansible_repo_folder" not in model["config"]["hortonworks"]:
            ERROR("Missing 'hortonworks.ansible_repo_folder' in configuration file")
        ansible_repo_folder = appendPath(os.path.dirname(model["data"]["configFile"]),  model["config"]["hortonworks"]["ansible_repo_folder"]) 
        model["config"]["hortonworks"]["ansible_repo_folder"] = ansible_repo_folder
        model["data"]["rolePaths"].add(appendPath(ansible_repo_folder, "roles"))
        return True
