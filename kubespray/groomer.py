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

