
import os
from misc import ERROR, setDefaultInMap, appendPath

def groom(plugin, model):
    repo_folder = appendPath(os.path.dirname(model["data"]["configFile"]),  model["config"]["kubespray"]["repo_folder"]) 
    model["config"]["kubespray"]["repo_folder"] = repo_folder
    model["data"]["rolePaths"].add(appendPath(repo_folder, "roles"))
    
    model["data"]["dnsNbrDots"] = model["cluster"]["domain"].count(".") + 1
