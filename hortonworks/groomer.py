
import os
from misc import ERROR, setDefaultInMap, appendPath,lookupRepository

def groom(plugin, model):
    setDefaultInMap(model["cluster"]["hortonworks"], "disabled", False)
    if model["cluster"]["hortonworks"]["disabled"]:
        return
    
    lookupRepository(model, "hortonworks") 
    
    ansible_repo_folder = appendPath(os.path.dirname(model["data"]["configFile"]),  model["config"]["hortonworks"]["ansible_repo_folder"]) 
    model["config"]["hortonworks"]["ansible_repo_folder"] = ansible_repo_folder
    model["data"]["rolePaths"].add(appendPath(ansible_repo_folder, "roles"))
