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
from misc import setDefaultInMap,appendPath,ERROR
from plugin import lookupPlugin

ANSIBLE="ansible"
CLUSTER="cluster"
PLAYBOOKS = "playbooks"
DISABLED = "disabled"
ROLES_PATHS="roles_paths"
DATA="data"
SOURCE_FILE_DIR = "sourceFileDir"
CONFIG="config"
ROLES_PATHS_FROM_PLUGINS="roles_paths_from_plugins"
ROLES="roles"
TAGS="tags"
FILE="file"

def groom(plugin, model):
    if ANSIBLE in model[CLUSTER]:
        setDefaultInMap(model[CLUSTER][ANSIBLE], DISABLED, False)
        if  model[CLUSTER][ANSIBLE][DISABLED]:
            return False
        if PLAYBOOKS in model[CLUSTER][ANSIBLE]:
            for idx in range(0, len(model[CLUSTER][ANSIBLE][PLAYBOOKS])):
                model[CLUSTER][ANSIBLE][PLAYBOOKS][idx][FILE] = appendPath(model[DATA][SOURCE_FILE_DIR], model[CLUSTER][ANSIBLE][PLAYBOOKS][idx][FILE])
                
        if ROLES_PATHS in model[CLUSTER][ANSIBLE]:
            for rp in model[CLUSTER][ANSIBLE][ROLES_PATHS]:
                model[DATA]["rolePaths"].add(appendPath(model[DATA][SOURCE_FILE_DIR], rp))
        if ROLES_PATHS_FROM_PLUGINS in model[CLUSTER][ANSIBLE]:
            for pluginName in model[CLUSTER][ANSIBLE][ROLES_PATHS_FROM_PLUGINS]:
                plugin = lookupPlugin(pluginName, model[CONFIG]["plugins_paths"])
                if plugin != None:
                    rolesPath = appendPath(plugin.path, "roles")
                    if os.path.exists(rolesPath):
                        model['data']["rolePaths"].add(rolesPath)
                    else:
                        ERROR("ansible.{}: There is no 'roles' folder in plugin '{}'".format(ROLES_PATHS_FROM_PLUGINS, pluginName))
                else:
                    ERROR("ansible.{}: plugin '{}' not found".format(ROLES_PATHS_FROM_PLUGINS, pluginName))
    if ANSIBLE in model[CONFIG] and ROLES_PATHS in model[CONFIG][ANSIBLE]:
        for rp in  model[CONFIG][ANSIBLE][ROLES_PATHS]:
            model[DATA]["rolePaths"].add(appendPath(os.path.dirname(model[DATA]["configFile"]), rp))
    return True
    