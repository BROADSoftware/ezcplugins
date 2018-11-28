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
import string
import random
import hashlib
from sets import Set


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
DATABASE="database"
TYPE="type"
MODE="mode"
SERVER="server"
ADD_REPO="add_repo"
POSTGRESQL_SERVER="postgresql_server"   # The group hosting postgresql server (Should contains only one host).
WEAK_PASSWORDS = "weak_passwords"
PASSWORDS = "passwords"
DATABASES="databases"
DATABASES_TO_CREATE = "databasesToCreate"
NODE_BY_NAME="nodeByName"
FQDN="fqdn"

def generatePassword():
    chars=string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for i in range(12))

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
        # ---------------------------- Handle database
        if model[CLUSTER][HORTONWORKS][DATABASE][TYPE] != "embedded":
            if MODE not in model[CLUSTER][HORTONWORKS][DATABASE]:
                ERROR("hostonworks.database.mode must be defined if type != 'embedded'!")
            if model[CLUSTER][HORTONWORKS][DATABASE][MODE] != "included" and model[CLUSTER][HORTONWORKS][DATABASE][TYPE] != 'postgres':
                ERROR("hostonworks.database: Only 'postgres' type is supported in 'internal' or 'external' mode ")
            if model[CLUSTER][HORTONWORKS][DATABASE][MODE] == 'external' and SERVER not in  model[CLUSTER][HORTONWORKS][DATABASE]:
                ERROR("hostonworks.database.server must be defined in 'external' mode ")
            if model[CLUSTER][HORTONWORKS][DATABASE][MODE] == 'internal' and SERVER in  model[CLUSTER][HORTONWORKS][DATABASE]:
                ERROR("hostonworks.database.server must NOT be defined in 'internal' mode ")
            setDefaultInMap(model[CLUSTER][HORTONWORKS][DATABASE], ADD_REPO, True)
            if model[CLUSTER][HORTONWORKS][DATABASE][MODE] == 'internal':
                if not POSTGRESQL_SERVER in model[DATA][GROUP_BY_NAME]:
                    ERROR("hostonworks.database.mode == 'internal', but no group '{}' was defined".format(POSTGRESQL_SERVER))
                srv = model[DATA][GROUP_BY_NAME][POSTGRESQL_SERVER][0]
                model[CLUSTER][HORTONWORKS][DATABASE][SERVER] = model[DATA][NODE_BY_NAME][srv][FQDN]
        # -------------------------------------------------Handle database
        # We need to create two layout.
        # - One to create databases and users on db server.
        # - One to provide info to group_vars/all
        setDefaultInMap(model[CLUSTER][HORTONWORKS], WEAK_PASSWORDS, False)
        setDefaultInMap(model[DATA], HORTONWORKS, {})
        setDefaultInMap(model[DATA][HORTONWORKS], DATABASES, {})
        setDefaultInMap(model, PASSWORDS, {})
        setDefaultInMap(model[PASSWORDS], DATABASES, {})
        tags = Set()
        tags.add("ambari")
        for role in model[CLUSTER][ROLES]:
            if HW_SERVICES in role:
                if "HIVE_METASTORE" in role[HW_SERVICES]:
                    tags.add("hive")
                if "OOZIE_SERVER" in role[HW_SERVICES]:
                    tags.add("oozie")
                if "DRUID_BROKER" in role[HW_SERVICES] or "DRUID_OVERLORD" in role[HW_SERVICES]:
                    tags.add("druid")
                if "SUPERSET" in role[HW_SERVICES]:
                    tags.add("superset")
                if "RANGER_ADMIN" in role[HW_SERVICES]:
                    tags.add("rangeradmin")
                if "RANGER_KMS_SERVER" in role[HW_SERVICES]:
                    tags.add("rangerkms")
                if "REGISTRY_SERVER" in role[HW_SERVICES]:
                    tags.add("registry")
                if "STREAMLINE_SERVER" in role[HW_SERVICES]:
                    tags.add("streamline")
        model[DATA][HORTONWORKS][DATABASES_TO_CREATE] = tags
        for tag in ["ambari", "hive", "oozie", "druid", "superset", "rangeradmin", "rangerkms", "registry", "streamline" ]:
            user = tag
            if model[CLUSTER][HORTONWORKS][WEAK_PASSWORDS]:
                password = user
            else:
                password = genaratePassword()
            md5Password = "md5" + hashlib.md5(password + user).hexdigest()
            model[DATA][HORTONWORKS][DATABASES][tag] = { 'user': user, 'database': tag, 'md5Password': md5Password }
            model[PASSWORDS][DATABASES][tag] = password
        return True
