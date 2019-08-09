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

from misc import ERROR,lookupSecurityContext,lookupRepository,setDefaultInMap,appendPath,lookupHelper
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
SECURITY_CONTEXT="security_context"
SECURITY="security"
SECURITY_CONTEXTS="security_contexts"
CONFIG="config"
ENVIRONMENT="environment"
EXTRA_ARGS="EXTRA_ARGS"
CONTEXT="context"
SUPER_USERS="super.users"

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

    security = 'none'
    setDefaultInMap(model[DATA], CONFLUENT, {})
    if CONFLUENT in model[CLUSTER]:

        # Get security context
        if SECURITY in model[CLUSTER][CONFLUENT]:
            if CONTEXT in model[CLUSTER][CONFLUENT][SECURITY]:
                model[CLUSTER][CONFLUENT][SECURITY_CONTEXT] = model[CLUSTER][CONFLUENT][SECURITY][CONTEXT] # TODO : review
                lookupSecurityContext(model, CONFLUENT)

                if "mit_kdc" in model[DATA][SECURITY_CONTEXTS][CONFLUENT] and "active_directory" in model[DATA][SECURITY_CONTEXTS][CONFLUENT]:
                    ERROR("Invalid context '{}.{}.{}' definition:  mit_kdc and active_directory are both defined, please keep only one !".format(SECURITY_CONTEXTS, CONFLUENT, model[DATA][SECURITY_CONTEXTS][CONFLUENT][NAME]))



                if "mit_kdc" in model[DATA][SECURITY_CONTEXTS][CONFLUENT]:
                    security = "mit_kdc"

                if "active_directory" in model[DATA][SECURITY_CONTEXTS][CONFLUENT]:
                    security = "active_directory"

                if security == 'none':
                    ERROR("Invalid context '{}.{}.{}' definition:  mit_kdc or active_directory should be defined".format(SECURITY_CONTEXTS, CONFLUENT, model[DATA][SECURITY_CONTEXTS][CONFLUENT][NAME]))

        # Merge confluent vars from cluster definition file (cluster.confluent)
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

    model[DATA][CONFLUENT][VARS] = all_vars
    model[DATA][CONFLUENT][SECURITY] = security
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

                mymap = {}
                mymap[KAFKA] = {}
                mymap[KAFKA][BROKER] = {}
                mymap[ZOOKEEPER] = {}

                if BROKER in cp_node[GROUPS]:
                    broker_id += 1
                    # Add broker id
                    mymap[KAFKA][BROKER][ID] = broker_id

                # Add the role specific value
                if BROKER in role:
                    if not isinstance(role[BROKER], dict):
                        ERROR("Invalid role definition ('{}'):  '{}' is not a dictionary".format(role[NAME], BROKER))
                    else:
                        mymap[KAFKA][BROKER] = schemaMerge(mymap[KAFKA][BROKER], role[BROKER])

                if ZOOKEEPER in role:
                    if not isinstance(role[ZOOKEEPER], dict):
                        ERROR("Invalid role definition ('{}'):  '{}' is not a dictionary".format(role[NAME], ZOOKEEPER))
                    else:
                        mymap[ZOOKEEPER] = schemaMerge(mymap[ZOOKEEPER], role[ZOOKEEPER])

                # And get the node specific value
                if BROKER in cp_node:
                    if not isinstance(cp_node[BROKER], dict):
                        ERROR("Invalid node definition in role '{}':  '{}.{}' is not a dictionary".format(role[NAME], cp_node[NAME], BROKER))
                    else:
                        mymap[KAFKA][BROKER] = schemaMerge(mymap[KAFKA][BROKER], cp_node[BROKER])

                if ZOOKEEPER in cp_node:
                    if not isinstance(cp_node[ZOOKEEPER], dict):
                        ERROR("Invalid node definition in role '{}':  '{}.{}' is not a dictionary".format(role[NAME], cp_node[NAME], ZOOKEEPER))
                    else:
                        mymap[ZOOKEEPER] = schemaMerge(mymap[ZOOKEEPER], cp_node[ZOOKEEPER])


                # if security is not 'none', enable SASL
                if security != 'none':
                    setDefaultInMap(mymap[ZOOKEEPER], CONFIG, {})
                    mymap[ZOOKEEPER][CONFIG]["authProvider.1"] = "org.apache.zookeeper.server.auth.SASLAuthenticationProvider"


                    zk_extra_args = ""
                    setDefaultInMap(mymap[ZOOKEEPER], ENVIRONMENT, {})
                    if EXTRA_ARGS in model[DATA][CONFLUENT][VARS][ZOOKEEPER][ENVIRONMENT]:
                        zk_extra_args = model[DATA][CONFLUENT][VARS][ZOOKEEPER][ENVIRONMENT][EXTRA_ARGS]

                    if EXTRA_ARGS in mymap[ZOOKEEPER][ENVIRONMENT]:
                        zk_extra_args = zk_extra_args + " " + mymap[ZOOKEEPER][ENVIRONMENT][EXTRA_ARGS]

                    zk_extra_args = zk_extra_args + " " + "-Djava.security.auth.login.config=/etc/kafka/zookeeper_server_jaas.conf" # Static path value

                    mymap[ZOOKEEPER][ENVIRONMENT][EXTRA_ARGS] = zk_extra_args

                    broker_extra_args = ""
                    setDefaultInMap(mymap[KAFKA][BROKER], ENVIRONMENT, {})
                    setDefaultInMap(mymap[KAFKA][BROKER], CONFIG, {})
                    if EXTRA_ARGS in model[DATA][CONFLUENT][VARS][KAFKA][BROKER][ENVIRONMENT]:
                        broker_extra_args = model[DATA][CONFLUENT][VARS][KAFKA][BROKER][ENVIRONMENT][EXTRA_ARGS]

                    if EXTRA_ARGS in mymap[KAFKA][BROKER][ENVIRONMENT]:
                        broker_extra_args = broker_extra_args + " " + mymap[KAFKA][BROKER][ENVIRONMENT][EXTRA_ARGS]

                    broker_extra_args = broker_extra_args + " " + "-Djava.security.auth.login.config=/etc/kafka/broker_server_jaas.conf" # Static path value

                    mymap[KAFKA][BROKER][ENVIRONMENT][EXTRA_ARGS] = broker_extra_args
                    mymap[KAFKA][BROKER][CONFIG][SUPER_USERS] = "User:kafka_" + model[CLUSTER][ID]
                    mymap[KAFKA][BROKER][CONFIG]["zookeeper.set.acl"] = "true"


                # Remove empty keys
                mymap[KAFKA] = dict( [(k,v) for k,v in mymap[KAFKA].items() if len(v)>0])
                mymap = dict( [(k,v) for k,v in mymap.items() if len(v)>0])

                if bool(mymap):
                    model[DATA][NODE_BY_NAME][cp_node[NAME]][CP_VARS] = mymap

    return True

