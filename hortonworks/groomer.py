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

HORTONWORKS = "hortonworks"
CLUSTER = "cluster"
DISABLED = "disabled"
CONFIG = "config"
ANSIBLE_REPO_FOLDER = "ansible_repo_folder"
DATA = "data"
CONFIG_FILE = "configFile"
ROLE_PATHS = "rolePaths"
EXTRA_GROUP_BY_NAME = "extraGroupByName"
HW_SERVICES = "hw_services"
NAME = "name"
NODES = "nodes"
ZOOKEEPERS = "zookeepers"
GROUP_BY_NAME = "groupByName"
KAFKA_BROKERS = "kafka_brokers"
ROLES="roles"
JAVA="java"
EMBEDDED="embedded"
ORACLEJDK="oraclejdk"
ORACLEJDK_TARBALL_LOCATION="oraclejdk_tarball_location"
ORACLEJDK_JCE_LOCATION="oraclejdk_jce_location"
REPOSITORIES="repositories"



def groom(plugin, model):
    setDefaultInMap(model[CLUSTER][HORTONWORKS], DISABLED, False)
    if model[CLUSTER][HORTONWORKS][DISABLED]:
        return False
    else:
        lookupRepository(model, HORTONWORKS) 
        if HORTONWORKS not in model[CONFIG] or ANSIBLE_REPO_FOLDER not in model[CONFIG][HORTONWORKS]:
            ERROR("Missing 'hortonworks.ansible_repo_folder' in configuration file")
        ansible_repo_folder = appendPath(os.path.dirname(model[DATA][CONFIG_FILE]),  model[CONFIG][HORTONWORKS][ANSIBLE_REPO_FOLDER]) 
        model[CONFIG][HORTONWORKS][ANSIBLE_REPO_FOLDER] = ansible_repo_folder
        model[DATA][ROLE_PATHS].add(appendPath(ansible_repo_folder, "roles"))
        # ------------- We need to define some groups for the intention of external tools.
        zookeepers = [] 
        kafka_brokers = []
        model[DATA][EXTRA_GROUP_BY_NAME] = {}
        for role in model[CLUSTER][ROLES]:
            if HW_SERVICES in role:
                if "ZOOKEEPER_SERVER" in role[HW_SERVICES]:
                    zookeepers.extend(map(lambda x : x[NAME], role[NODES]))
                if "KAFKA_BROKER" in role[HW_SERVICES]:
                    kafka_brokers.extend(map(lambda x : x[NAME], role[NODES]))
        if ZOOKEEPERS not in model[DATA][GROUP_BY_NAME]:
            model[DATA][EXTRA_GROUP_BY_NAME][ZOOKEEPERS] = zookeepers
        if KAFKA_BROKERS not in model[DATA][GROUP_BY_NAME]:
            model[DATA][EXTRA_GROUP_BY_NAME][KAFKA_BROKERS] = kafka_brokers
        # ---------------------------- Handle java
        #setDefaultInMap(model[CLUSTER][HORTONWORKS], JAVA, EMBEDDED)
        if model[CLUSTER][HORTONWORKS][JAVA] == ORACLEJDK:
            if ORACLEJDK_TARBALL_LOCATION not in model[DATA][REPOSITORIES][HORTONWORKS]:
                ERROR("'hortonworks.java' is set to 'oraclejdk' while there is no 'repositories.hortonworks.oraclejdk_tarball_location' defined in configuration file!")
            if ORACLEJDK_JCE_LOCATION not in model[DATA][REPOSITORIES][HORTONWORKS]:
                ERROR("'hortonworks.java' is set to 'oraclejdk' while there is no 'repositories.hortonworks.oraclejdk_jce_location' defined in configuration file!")
        return True
