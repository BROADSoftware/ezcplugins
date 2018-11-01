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
        # We need to define some groups for the intention of external tools.
        zookeepers = [] 
        kafka_brokers = []
        model["data"]["extraGroupByName"] = {}
        for role in model["cluster"]["roles"]:
            if "hw_services" in role:
                if "ZOOKEEPER_SERVER" in role["hw_services"]:
                    zookeepers.extend(map(lambda x : x["name"], role["nodes"]))
                if "KAFKA_BROKER" in role["hw_services"]:
                    kafka_brokers.extend(map(lambda x : x["name"], role["nodes"]))
        if "zookeepers" not in model["data"]["groupByName"]:
            model["data"]["extraGroupByName"]["zookeepers"] = zookeepers
        if "kafka_brokers" not in model["data"]["groupByName"]:
            model["data"]["extraGroupByName"]["kafka_brokers"] = kafka_brokers
        return True
