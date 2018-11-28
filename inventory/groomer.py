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
import os
from misc import ERROR,setDefaultInMap,appendPath
import ipaddress
import yaml

INVENTORY="inventory"
DEFAULTS="defaults"
CLUSTER="cluster"
NODES="nodes"
NAME="name"

ANSIBLE_USER="ansible_user"
ANSIBLE_BECOME="ansible_become"
ANSIBLE_PRIVATE_KEY="ansible_private_key"

DATA="data"
SOURCE_FILE_DIR="sourceFileDir"

def groom(plugin, model):
    for node in model[CLUSTER][NODES]:
        if ANSIBLE_USER not in node:
            if INVENTORY not in model[CLUSTER] or ANSIBLE_USER not in model[CLUSTER][INVENTORY][DEFAULTS]:
                ERROR("'{}' is not defined either in node '{}' and in inventory.defaults!".format(ANSIBLE_USER, node[NAME]))
            else:
                node[ANSIBLE_USER] = model[CLUSTER][INVENTORY][DEFAULTS][ANSIBLE_USER]
        if ANSIBLE_BECOME not in node:
            if INVENTORY not in model[CLUSTER] or ANSIBLE_BECOME not in model[CLUSTER][INVENTORY][DEFAULTS]:
                ERROR("'{}' is not defined either in node '{}' and in inventory.defaults!".format(ANSIBLE_BECOME, node[NAME]))
            else:
                node[ANSIBLE_BECOME] = model[CLUSTER][INVENTORY][DEFAULTS][ANSIBLE_BECOME]
        if ANSIBLE_PRIVATE_KEY not in node:
            if INVENTORY not in model[CLUSTER] or ANSIBLE_PRIVATE_KEY not in model[CLUSTER][INVENTORY][DEFAULTS]:
                ERROR("'{}' is not defined either in node '{}' and in inventory.defaults!".format(ANSIBLE_PRIVATE_KEY, node[NAME]))
            else:
                node[ANSIBLE_PRIVATE_KEY] = model[CLUSTER][INVENTORY][DEFAULTS][ANSIBLE_PRIVATE_KEY]
        node[ANSIBLE_PRIVATE_KEY] = appendPath(model[DATA][SOURCE_FILE_DIR], node[ANSIBLE_PRIVATE_KEY])
        if not os.path.isfile(node[ANSIBLE_PRIVATE_KEY]) or not os.access(node[ANSIBLE_PRIVATE_KEY], os.R_OK):
            ERROR("Node '{}': Invalid private key path:'{}'".format(node[NAME], node[ANSIBLE_PRIVATE_KEY]))
    model["data"]["buildScript"] = appendPath(model["data"]["targetFolder"], "build.sh")
    return True # Always enabled
        