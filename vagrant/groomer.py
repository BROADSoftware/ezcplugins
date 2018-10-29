

import logging
import os
from misc import ERROR,setDefaultInMap,appendPath
import ipaddress
import yaml


loggerConfig = logging.getLogger("ezcluster.config")

       
SYNCED_FOLDERS="synced_folders"

def groom(plugin, model):
    if 'core' not in model["cluster"]["plugins"]:
        ERROR("Plugin 'core' is mandatory before plugin 'vagrant'")

    repoInConfig = "repositories" in model["config"] and "repo_yum_base_url" in model["config"]["repositories"]
    setDefaultInMap(model["cluster"]["vagrant"], "local_yum_repo", repoInConfig)
    if model["cluster"]["vagrant"]["local_yum_repo"] and not repoInConfig:
        ERROR("'repositories.repo_yum_base_url' is not defined in config file while 'vagrant.local_yum_repo' is set to True")
        
    for node in model['cluster']['nodes']:
        if not SYNCED_FOLDERS in node:
            node[SYNCED_FOLDERS] = []
        role = model["data"]["roleByName"][node["role"]]
        if SYNCED_FOLDERS in role:
            node[SYNCED_FOLDERS] += role[SYNCED_FOLDERS]
        if SYNCED_FOLDERS in model["cluster"]["vagrant"]:
            node[SYNCED_FOLDERS] += model["cluster"]["vagrant"][SYNCED_FOLDERS]
    
    model["data"]["buildScript"] = appendPath(model["data"]["targetFolder"], "build.sh")
    return True # Always enabled
        