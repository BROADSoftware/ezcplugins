
import os
from misc import ERROR,lookupRepository,setDefaultInMap,appendPath


def groom(plugin, model):
    setDefaultInMap(model["cluster"]["confluent"], "disabled", False)
    if model["cluster"]["confluent"]["disabled"]:
        return
    
    lookupRepository(model, "confluent")
    
    for node in model['cluster']['nodes']:
        if "kafka_log_dirs" in node:
            if len(node["kafka_log_dirs"]) == 0:
                del(node["kafka_log_dirs"])
        else:
            if "kafka_log_dirs" in model["data"]["roleByName"][node["role"]]:
                node["kafka_log_dirs"] = model["data"]["roleByName"][node["role"]]["kafka_log_dirs"]
    
    ansible_repo_folder = appendPath(os.path.dirname(model["data"]["configFile"]),  model["config"]["confluent"]["ansible_repo_folder"]) 
    model["config"]["confluent"]["ansible_repo_folder"] = ansible_repo_folder
    model["data"]["rolePaths"].add(appendPath(ansible_repo_folder, "roles"))
    
    # We need to define an ansible group "preflight" hosting all nodes 
    preflight = []
    for node in model["cluster"]["nodes"]:
        preflight.append(node["name"])
    model["data"]["groupByName"]["preflight"] = preflight


