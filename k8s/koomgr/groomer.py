# Copyright (C) 2020 BROADSoftware
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


CLUSTER = "cluster"
DATA="data"
K8S="k8s"
KOOMGR="koomgr"
DISABLED = "disabled"
SSL_CERT_SRC="ssl_cert_src"
SSL_KEY_SRC="ssl_key_src"
SOURCE_FILE_DIR="sourceFileDir"
CONFIG="config"
PROVIDERS="providers"
STATIC_PROVIDERS="static_providers"
NAME="name"
PROVIDERS="providers"
TYPE="type"
LDAP_PROVIDERS="ldap_providers"
ROOTCA="rootCA"
CONFIG_FILE="configFile"
SRC_PATH="srcPath"
BASENAME="basename"
LOG_LEVEL="log_level"
LOG_MODE="log_mode"
ADMIN_GROUP="admin_group"
CRD_PROVIDERS="crd_providers"
LOCAL_MANIFESTS="local_manifests"
CRD="crd"
DEPLOY="deploy"
RBAC="rbac"

def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER], K8S, {})
    setDefaultInMap(model[CLUSTER][K8S], KOOMGR, {})
    setDefaultInMap(model[CLUSTER][K8S][KOOMGR], DISABLED, False)   
    if model[CLUSTER][K8S][KOOMGR][DISABLED]:
        return False
    else:
        setDefaultInMap(model[CLUSTER][K8S][KOOMGR], LOG_LEVEL, 0)
        setDefaultInMap(model[CLUSTER][K8S][KOOMGR], LOG_MODE, "json")
        setDefaultInMap(model[CLUSTER][K8S][KOOMGR], ADMIN_GROUP,  "kooadmin")

        setDefaultInMap(model[DATA], K8S, {})
        setDefaultInMap(model[DATA][K8S],KOOMGR, {})
        
        if model[CLUSTER][K8S][KOOMGR][LOG_LEVEL] > 0 and model[CLUSTER][K8S][KOOMGR][LOG_MODE] == "json":
            ERROR("logLevel can't be greater than one when logMode is 'json'. Set 'log_mode' to 'dev'")
                    
        providerByName = {}
        if KOOMGR in model[CONFIG]:
            if STATIC_PROVIDERS in model[CONFIG][KOOMGR]:
                for prvd in model[CONFIG][KOOMGR][STATIC_PROVIDERS]:
                    prvd[TYPE] = "static"
                    if prvd[NAME] in providerByName:
                        ERROR("There is two providers of name '{}'".format(prvd[NAME]))
                    providerByName[prvd[NAME]] = prvd
            if LDAP_PROVIDERS in model[CONFIG][KOOMGR]:
                for prvd in model[CONFIG][KOOMGR][LDAP_PROVIDERS]:
                    prvd[TYPE] = "ldap"
                    if prvd[NAME] in providerByName:
                        ERROR("There is two providers of name '{}'".format(prvd[NAME]))
                    providerByName[prvd[NAME]] = prvd
                    if ROOTCA in prvd:
                        prvd[ROOTCA] = appendPath(os.path.dirname(model[DATA][CONFIG_FILE]), prvd[ROOTCA])
                        if not os.path.isfile( prvd[ROOTCA]):
                            ERROR("Unable to find '{}'!".format( prvd[ROOTCA]))
            if CRD_PROVIDERS in model[CONFIG][KOOMGR]:
                for prvd in model[CONFIG][KOOMGR][CRD_PROVIDERS]:
                    prvd[TYPE] = "crd"
                    if prvd[NAME] in providerByName:
                        ERROR("There is two providers of name '{}'".format(prvd[NAME]))
                    providerByName[prvd[NAME]] = prvd
        if LOCAL_MANIFESTS in model[CLUSTER][K8S][KOOMGR]:
            model[CLUSTER][K8S][KOOMGR][LOCAL_MANIFESTS][CRD] = appendPath(model[DATA][SOURCE_FILE_DIR], model[CLUSTER][K8S][KOOMGR][LOCAL_MANIFESTS][CRD])
            if not os.path.isfile( model[CLUSTER][K8S][KOOMGR][LOCAL_MANIFESTS][CRD]):
                ERROR("Unable to find '{}'!".format( model[CLUSTER][K8S][KOOMGR][LOCAL_MANIFESTS][CRD]))
    
            model[CLUSTER][K8S][KOOMGR][LOCAL_MANIFESTS][DEPLOY] = appendPath(model[DATA][SOURCE_FILE_DIR], model[CLUSTER][K8S][KOOMGR][LOCAL_MANIFESTS][DEPLOY])
            if not os.path.isfile( model[CLUSTER][K8S][KOOMGR][LOCAL_MANIFESTS][DEPLOY]):
                ERROR("Unable to find '{}'!".format( model[CLUSTER][K8S][KOOMGR][LOCAL_MANIFESTS][DEPLOY]))
    
            model[CLUSTER][K8S][KOOMGR][LOCAL_MANIFESTS][RBAC] = appendPath(model[DATA][SOURCE_FILE_DIR], model[CLUSTER][K8S][KOOMGR][LOCAL_MANIFESTS][RBAC])
            if not os.path.isfile( model[CLUSTER][K8S][KOOMGR][LOCAL_MANIFESTS][RBAC]):
                ERROR("Unable to find '{}'!".format( model[CLUSTER][K8S][KOOMGR][LOCAL_MANIFESTS][RBAC]))
                    
        model[DATA][K8S][KOOMGR][PROVIDERS] = []
        for pname in model[CLUSTER][K8S][KOOMGR][PROVIDERS]:
            if pname not in providerByName:
                ERROR("Provider '{}' does not exists in global configuration file!".format(pname))
            prvd = providerByName[pname]
            model[DATA][K8S][KOOMGR][PROVIDERS].append(prvd)
            
        return True
