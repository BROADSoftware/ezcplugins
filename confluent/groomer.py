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

import os
from misc import ERROR,lookupRepository,setDefaultInMap,appendPath


def groom(plugin, model):
    setDefaultInMap(model["cluster"]["confluent"], "disabled", False)
    if model["cluster"]["confluent"]["disabled"]:
        return False
    
    lookupRepository(model, "confluent")
    if "confluent" not in model["config"] or "ansible_repo_folder" not in model["config"]["confluent"]:
        ERROR("Missing 'confluent.ansible_repo_folder' in configuration file")
    
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
    return True

