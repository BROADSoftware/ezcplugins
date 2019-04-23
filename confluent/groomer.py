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

from misc import ERROR,lookupRepository,setDefaultInMap,appendPath,lookupHelper
import os
import yaml
from schema import schemaMerge

CONFLUENT="confluent"
DATA="data"
HELPERS="helpers"
FOLDER="folder"
ROLE_PATHS = "rolePaths"
PLAYBOOK_VARS="playbook_vars"
CLUSTER="cluster"
CONFLUENT="confluent"
CP_NODES="cpNodes"
NODES="nodes"
ROLES="roles"
NAME="name"
VARS="vars"
ROLE="role"
NODE_BY_NAME="nodeByName"
KAFKA="kafka"
BROKER="broker"
ID="id"
GROUP_BY_NAME="groupByName"
DISABLED="disabled"
KAFKA_LOG_DIRS="kafka_log_dirs"
ROLE_BY_NAME="roleByName"
PREFLIGHT="preflight"
GROUPS="groups"
ZOOKEEPER="zookeeper"
CP_VARS="cp_vars"
def groom(plugin, model):
    setDefaultInMap(model[CLUSTER][CONFLUENT], DISABLED, False)
    if model[CLUSTER][CONFLUENT][DISABLED]:
        return False
    
    lookupRepository(model, CONFLUENT)
    lookupHelper(model, CONFLUENT)
    model[DATA][ROLE_PATHS].add(appendPath(model[DATA][HELPERS][CONFLUENT][FOLDER], ROLES))

    # We need to define an ansible group "preflight" hosting all nodes
    preflight = []
    for node in model[CLUSTER][NODES]:
        preflight.append(node[NAME])
    model[DATA][GROUP_BY_NAME][PREFLIGHT] = preflight

    f = os.path.join(plugin.path, "default.yml")
    if os.path.exists(f):
        all_vars = yaml.load(open(f))
    else:
        all_vars = {}

    # Merge confluent vars from cluster definition file (cluster.confluent)
    if CONFLUENT in model[CLUSTER]:
        # Get broker vars
        if BROKER in model[CLUSTER][CONFLUENT]:
            if not isinstance(model[CLUSTER][CONFLUENT][BROKER], dict):
                ERROR("Invalid global '{}.{}' definition:  not a dictionary".format(CONFLUENT, BROKER))
            else:
                all_vars[KAFKA][BROKER] = schemaMerge(all_vars[KAFKA][BROKER], model[CLUSTER][CONFLUENT][BROKER])
        # Get zookeeper vars
        if ZOOKEEPER in model[CLUSTER][CONFLUENT]:
            if not isinstance(model[CLUSTER][CONFLUENT][ZOOKEEPER], dict):
                ERROR("Invalid global '{}.{}' definition:  not a dictionary".format(CONFLUENT, ZOOKEEPER))
            else:
                all_vars[ZOOKEEPER] = schemaMerge(all_vars[ZOOKEEPER], model[CLUSTER][CONFLUENT][ZOOKEEPER])

    model[CLUSTER][CONFLUENT][VARS] = all_vars

    """ 
    For each node, will merge confluent vars from:
    - parent role
    - node """

    broker_id = 0
    for role in model[CLUSTER][ROLES]:
        if NODES in role:
            index = -1
            for cp_node in role[NODES]:
                index += 1

                map = {}
                map[KAFKA] = {}
                map[KAFKA][BROKER] = {}
                map[ZOOKEEPER] = {}

                if BROKER in cp_node[GROUPS]:
                    broker_id += 1
                    # Add broker id
                    map[KAFKA][BROKER][ID] = broker_id

                # Add the role specific value
                if BROKER in role:
                    if not isinstance(role[BROKER], dict):
                        ERROR("Invalid role definition ('{}'):  '{}' is not a dictionary".format(role[NAME], BROKER))
                    else:
                        map[KAFKA][BROKER] = schemaMerge(map[KAFKA][BROKER], role[BROKER])

                if ZOOKEEPER in role:
                    if not isinstance(role[ZOOKEEPER], dict):
                        ERROR("Invalid role definition ('{}'):  '{}' is not a dictionary".format(role[NAME], ZOOKEEPER))
                    else:
                        map[ZOOKEEPER] = schemaMerge(map[ZOOKEEPER], role[ZOOKEEPER])

                # And get the node specific value
                if BROKER in cp_node:
                    if not isinstance(cp_node[BROKER], dict):
                        ERROR("Invalid node definition in role '{}':  '{}.{}' is not a dictionary".format(role[NAME], cp_node[NAME], BROKER))
                    else:
                        map[KAFKA][BROKER] = schemaMerge(map[KAFKA][BROKER], cp_node[BROKER])

                if ZOOKEEPER in cp_node:
                    if not isinstance(cp_node[ZOOKEEPER], dict):
                        ERROR("Invalid node definition in role '{}':  '{}.{}' is not a dictionary".format(role[NAME], cp_node[NAME], ZOOKEEPER))
                    else:
                        map[ZOOKEEPER] = schemaMerge(map[ZOOKEEPER], cp_node[ZOOKEEPER])

                # Remove empty keys
                map[KAFKA] = dict( [(k,v) for k,v in map[KAFKA].items() if len(v)>0])
                map = dict( [(k,v) for k,v in map.items() if len(v)>0])

                if bool(map):
                    model[DATA][NODE_BY_NAME][cp_node[NAME]][CP_VARS] = map

    return True

