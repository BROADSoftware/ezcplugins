# Copyright (C) 2018 BROADSoftware
#
# This file is part of EzCluster
#
# EzCluster is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EzCluster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with EzCluster.  If not, see <http://www.gnu.org/licenses/lgpl-3.0.html>.


import logging
from misc import ERROR,setDefaultInMap,appendPath
import copy

loggerConfig = logging.getLogger("ezcluster.config")

       
SYNCED_FOLDERS="synced_folders"


deviceFromIndex = [ 'sdb', 'sdc', 'sdd', 'sde', 'sdf', 'sdg', 'sdh', 'sdi', 'sdj', 'sdk', 'sdl', 'sdm', 'sdn', 'sdo', 'sdp', 'sdq', 'sdr', 'sds', 'sdt', 'sdu', 'sdv' ]


def groomRoles(model):
    # Handle data disks            
    for rl in model["cluster"]["roles"]:
        role = model["data"]["roleByName"][rl["name"]]
        if "data_disks" in role:
            for i in range(0, len(role['data_disks'])):
                role['data_disks'][i]['port'] = i + 1
                role['data_disks'][i]['device'] = deviceFromIndex[i]
            disksToMount = 0
            for d in role['data_disks']:
                if "mount" in d:
                    disksToMount += 1
            role["disksToMountCount"] = disksToMount
        else:
            role["disksToMountCount"] = 0

def groomNodes(model):
    model['data']['dataDisksByNode'] = {}
    for node in model['cluster']['nodes']:
        if not SYNCED_FOLDERS in node:
            node[SYNCED_FOLDERS] = []
        role = model["data"]["roleByName"][node["role"]]
        if SYNCED_FOLDERS in role:
            node[SYNCED_FOLDERS] += role[SYNCED_FOLDERS]
        if SYNCED_FOLDERS in model["cluster"]["vagrant"]:
            node[SYNCED_FOLDERS] += model["cluster"]["vagrant"][SYNCED_FOLDERS]
        if "data_disks" in role:
            dataDisks = copy.deepcopy(role['data_disks'])
            for disk in dataDisks:
                disk["fileName"] = "../disks/{}_{}.vmdk".format(node["name"], disk["device"])
                disk["size_mb"] = disk["size"] * 1024
            model['data']['dataDisksByNode'][node["name"]] = dataDisks

def groom(_plugin, model):
    repoInConfig = "repositories" in model["config"] and "vagrant" in model["config"]["repositories"]  and "yum_repo_base_url" in model["config"]["repositories"]["vagrant"]
    if model["cluster"]["vagrant"]["yum_repo"] == "local" and not repoInConfig:
        ERROR("'repositories.vagrant.repo_yum_base_url' is not defined in config file while 'vagrant.yum_repo' is set to 'local' in '{}'".format(model["data"]["sourceFileDir"]))
    if repoInConfig:
        # All plugins are lookinhg up their repositories in model["data"]. So does the vagrant one.
        setDefaultInMap(model["data"], "repositories", {})
        setDefaultInMap(model["data"]["repositories"], "vagrant", {})
        model["data"]["repositories"]["vagrant"]["yum_repo_base_url"] = model["config"]["repositories"]["vagrant"]["yum_repo_base_url"]

    groomRoles(model)
    groomNodes(model)
        
    model["data"]["buildScript"] = appendPath(model["data"]["targetFolder"], "build.sh")
    return True # Always enabled
        