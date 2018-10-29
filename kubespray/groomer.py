
import os
from misc import ERROR, setDefaultInMap, appendPath

def groom(plugin, model):
    setDefaultInMap(model["cluster"], "kubespray", {})
    setDefaultInMap(model["cluster"]["kubespray"], "disabled", False)
    if model["cluster"]["kubespray"]["disabled"]:
        return False
    else:
        if "kubespray" not in model["config"] or "ansible_repo_folder" not in model["config"]["kubespray"]:
            ERROR("Missing 'kubespray.ansible_repo_folder' in configuration file")
        ansible_repo_folder = appendPath(os.path.dirname(model["data"]["configFile"]),  model["config"]["kubespray"]["ansible_repo_folder"]) 
        model["config"]["kubespray"]["ansible_repo_folder"] = ansible_repo_folder
        model["data"]["rolePaths"].add(appendPath(ansible_repo_folder, "roles"))
        
        model["data"]["dnsNbrDots"] = model["cluster"]["domain"].count(".") + 1
        return True

