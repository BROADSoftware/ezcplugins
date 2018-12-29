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
import yaml
from vault import getVault


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
HW_PASSWORDS = "hwPasswords"
DATABASES="databases"
DATABASES_TO_CREATE = "databasesToCreate"
NODE_BY_NAME="nodeByName"
FQDN="fqdn"
SOURCE_FILE_DIR="sourceFileDir"
from pykwalify.core import Core as kwalify


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
        setDefaultInMap(model, HW_PASSWORDS, {})
        setDefaultInMap(model[HW_PASSWORDS], DATABASES, {})
        toCreateDbSet = Set()
        toCreateDbSet.add("ambari")
        for role in model[CLUSTER][ROLES]:
            if HW_SERVICES in role:
                if "HIVE_METASTORE" in role[HW_SERVICES]:
                    toCreateDbSet.add("hive")
                if "OOZIE_SERVER" in role[HW_SERVICES]:
                    toCreateDbSet.add("oozie")
                if "DRUID_BROKER" in role[HW_SERVICES] or "DRUID_OVERLORD" in role[HW_SERVICES]:
                    toCreateDbSet.add("druid")
                if "SUPERSET" in role[HW_SERVICES]:
                    toCreateDbSet.add("superset")
                if "RANGER_ADMIN" in role[HW_SERVICES]:
                    toCreateDbSet.add("rangeradmin")
                if "RANGER_KMS_SERVER" in role[HW_SERVICES]:
                    toCreateDbSet.add("rangerkms")
                if "REGISTRY_SERVER" in role[HW_SERVICES]:
                    toCreateDbSet.add("registry")
                if "STREAMLINE_SERVER" in role[HW_SERVICES]:
                    toCreateDbSet.add("streamline")
        model[DATA][HORTONWORKS][DATABASES_TO_CREATE] = toCreateDbSet
        wallet = loadWallet(plugin, model, toCreateDbSet)   
        model[HW_PASSWORDS] = wallet
        for db in wallet[DATABASES]:
            user = db
            password = wallet[DATABASES][db]
            md5Password = "md5" + hashlib.md5(password + user).hexdigest()
            model[DATA][HORTONWORKS][DATABASES][db] = { 'user': user, 'database': db, 'md5Password': md5Password }
        # We generate passwords for all db, even if unused, as they will be set in template
        for db in ["ambari", "hive", "oozie", "druid", "superset", "rangeradmin", "rangerkms", "registry", "streamline" ]:
            if db not in model[DATA][HORTONWORKS][DATABASES]:
                user = db
                md5Password = "md5" + hashlib.md5('unused' + user).hexdigest()
                model[DATA][HORTONWORKS][DATABASES][db] = { 'user': db, 'database': db, 'md5Password': md5Password }
            if db not in model[HW_PASSWORDS][DATABASES]:
                model[HW_PASSWORDS][DATABASES][db] = "unused"
        return True


def generatePassword():
    chars=string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for i in range(12))

def loadWallet(plugin, model, toCreateDbSet):
    wfname = appendPath(model[DATA][SOURCE_FILE_DIR], "wallet.yml")
    if os.path.exists(wfname):
        print ("\nWill reuse password from '{}'".format(wfname))
        data, was_encrypted = getVault().encryptedFile2String(wfname)
        wallet = yaml.load(data)
        walletSchema = yaml.load(open(os.path.join(plugin.path, "wallet-schema.yml")))
        k = kwalify(source_data = wallet, schema_data=walletSchema)
        k.validate(raise_exception=False)
        if len(k.errors) != 0:
            ERROR("Problem in {0}: {1}".format(wfname, k.errors))
        if wallet[WEAK_PASSWORDS] != model[CLUSTER][HORTONWORKS][WEAK_PASSWORDS]:
            ERROR("Hortonworks: 'weak_passwords' value are not in sync between wallet.yml and cluster definition file!")
        # Ensure all DB to create got an effective password:
        for db in toCreateDbSet:
            if db not in wallet[DATABASES]:
                ERROR("Hortonworks: Wallet is missing effective password for database '{}'".format(db))
        if "rangeradmin" in toCreateDbSet and "ranger_admin" not in wallet:
            ERROR("Hortonworks: Missing 'ranger_admin' password in Wallet while RANGER service is defined")
        if not was_encrypted:
            print("'{}' was not encrypted. Will encrypt it".format(wfname))
            getVault().stringToEncryptedFile(data, wfname)
    else:
        wallet = {}
        weakp = wallet[WEAK_PASSWORDS] = model[CLUSTER][HORTONWORKS][WEAK_PASSWORDS]
        wallet[DATABASES] = {}
        for db in toCreateDbSet:
            wallet[DATABASES][db] = db if weakp else generatePassword()
        wallet["ambari_admin"] = "admin" if weakp else generatePassword()
        wallet["default"] = "default2018" if weakp else generatePassword()
        if "rangeradmin" in db:
            wallet["ranger_admin"] = "admin" if weakp else generatePassword()
        #print(wallet)
        data = yaml.dump(wallet, width=10240,  indent=4, allow_unicode=True, default_flow_style=False)
        getVault().stringToEncryptedFile(data, wfname)
        print ("\nNew passwords has been generated in '{}'".format(wfname))
    return wallet

def dump(plugin, model, dumper):
    if HW_PASSWORDS in model and dumper.unsafe:
        dumper.dump("hw-passwords.json", model[HW_PASSWORDS])
