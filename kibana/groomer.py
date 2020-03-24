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
import copy
import yaml
from misc import ERROR,setDefaultInMap,lookupRepository,lookupHelper
from schema import schemaMerge


CLUSTER="cluster"
CONFIG="config"
KIBANA="kibana"
ROLE="role"
DATA="data"
NAME="name"
DISABLED="disabled"
VERSION="version"
ES_NODES="es_nodes"
ROLES="roles"
ES_CONFIG="es_config"
NODE_MASTER="node.master"
NODE_DATA="node.data"
VARS="vars"
NODE_BY_NAME="nodeByName"
NODES="nodes"
GROUP_BY_NAME="groupByName"
REPOSITORIES="repositories"
ROLE_PATHS="rolePaths"
HELPERS="helpers"
FOLDER="folder"
NODES="nodes"
PLAYBOOK_VARS="playbook_vars"
KIBANA_PLAYBOOK_VARS="kibana_playbook_vars"
ES_VERSION="es_version"
ES_MAJOR_VERSION="es_major_version"
KBNODES="kbNodes"
def groom(plugin, model):
    
    setDefaultInMap(model[CLUSTER][KIBANA], DISABLED, False)
    if model[CLUSTER][KIBANA][DISABLED]:
        return False
    lookupRepository(model, KIBANA)
    lookupHelper(model, KIBANA)
    model[DATA][ROLE_PATHS].add(model[DATA][HELPERS][KIBANA][FOLDER])
    f = os.path.join(plugin.path, "default.yml")
    if os.path.exists(f):
        base = yaml.load(open(f))
    else:
        base = {}
        
    model[DATA][KBNODES] = []
    """ 
    For each kb_node, will merge kibana vars from:
    - Plugin default configuration file
    - global from cluster definition file
    - parent role 
    - nodes definition
    """

    for role in model[CLUSTER][ROLES]:
        if KIBANA in role:
            # Get global value
            global_conf = {}
            if KIBANA in model[CLUSTER] and PLAYBOOK_VARS in model[CLUSTER][KIBANA]:
                if not isinstance(model[CLUSTER][KIBANA][PLAYBOOK_VARS], dict):
                    ERROR("Invalid global '{}.{}' definition:  not a dictionary".format(KIBANA, PLAYBOOK_VARS))
                else:
                    global_conf = schemaMerge(global_conf, model[CLUSTER][KIBANA][PLAYBOOK_VARS])

            # Get the role specific value
            role_conf = {}
            if PLAYBOOK_VARS in role[KIBANA]:
                if not isinstance(role[KIBANA][PLAYBOOK_VARS], dict):
                    ERROR("Invalid role definition ('{}'):  '{}.{}' is not a dictionary".format(role[NAME], KIBANA,PLAYBOOK_VARS))
                else:
                    role_conf = schemaMerge(role_conf, role[KIBANA][PLAYBOOK_VARS])

            for kb_node in role[NODES]:
                mymap = copy.deepcopy(base)
                # Add repository info.  There is two reasons to use a package url:
                # - It will be faster if the repo is local
                # - Seems yum install is bugged on current role:
                #     TASK [ansible-elasticsearch : RedHat - Install Elasticsearch] **************************************************************************************************
                #     fatal: [w2]: FAILED! => {"msg": "The conditional check 'redhat_elasticsearch_install_from_repo.rc == 0' failed. The error was: error while evaluating conditional (redhat_elasticsearch_install_from_repo.rc == 0): 'dict object' has no attribute 'rc'"}
                mymap["kibana_custom_package_url"] = model[DATA][REPOSITORIES][KIBANA]["kibana_package_url"]
                mymap["es_use_repository"] = False
                # Add global conf
                mymap = schemaMerge(mymap, global_conf)
                # Add role conf
                mymap = schemaMerge(mymap, role_conf)

                # Add node specific conf
                if KIBANA in kb_node and PLAYBOOK_VARS in kb_node[KIBANA]:
                    if not isinstance(kb_node[KIBANA][PLAYBOOK_VARS], dict):
                        ERROR("Invalid role definition ('{}'):  '{}.{}.{}' is not a dictionary".format(role[NAME], kb_node[NAME], KIBANA, PLAYBOOK_VARS))
                    else:
                        mymap = schemaMerge(mymap, kb_node[KIBANA][PLAYBOOK_VARS])

                mymap[ES_VERSION] = model[DATA][REPOSITORIES][KIBANA][VERSION]
                mymap[ES_MAJOR_VERSION] = mymap[ES_VERSION][:2] + "X"
                model[DATA][NODE_BY_NAME][kb_node[NAME]][KIBANA_PLAYBOOK_VARS] = mymap

            kbn = {}
            kbn[ROLE] = role[NAME]
            kbn[VARS] = schemaMerge(global_conf, role_conf)
            model[DATA][KBNODES].append(kbn)
    return True

            
