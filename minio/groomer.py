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

from misc import setDefaultInMap,ERROR, appendPath
import re
import os
from sets import Set

CLUSTER = "cluster"
DISABLED = "disabled"
MINIO="minio"
TENANTS="tenants"
POOLS="pools"
DATA="data"
ANSIBLE_NAME_BY_FQDN="ansibleNameByFqdn"
ANSIBLE_NAMES="ansibleNames"
FQDN="fqdn"
NAME="name"
NODES="nodes"
VOLUMES="volumes"
SCHEME="scheme"
BIND_ADDRESS="bind_address"
BIND_PORT="bind_port"
USER="user"
GROUP="group"
POOL_EXTS="poolExts"
DEFINITION="definition"
PARSED="parsed"
REPOSITORIES="repositories"
REPOSITORY="repository"
REPO_ID="repo_id" 
CONSOLE="console"
TLS_CRT="tls_crt"
TLS_KEY="tls_key"
SERVER_CA="server_ca"
SOURCE_FILE_DIR="sourceFileDir"
TLS_BIND_PORT="tls_bind_port"


poolRegex = re.compile('(http[s]?)://([^{]*){([0-9]+)\.\.\.([0-9]+)}([^/]*)/([^{]*){([0-9]+)\.\.\.([0-9]+)}(.*)')


def parse_pool(model, pool):
    #print("pool:{}".format(pool))
    m = poolRegex.match(pool)
    if not m:
        ERROR("Invalid pool value: {}".format(pool))
    else:
        scheme = m.group(1)
        host_prefix = m.group(2)
        host_first_idx = int(m.group(3))
        host_last_idx = int(m.group(4))
        host_postfix = m.group(5)
        volume_prefix = "/" + m.group(6)
        volume_first_idx = int(m.group(7))
        volume_last_idx = int(m.group(8))
        volume_postfix = m.group(9)
        pool_desc = { SCHEME: scheme, ANSIBLE_NAMES: [], VOLUMES: [] }
        for idx in range(host_first_idx, host_last_idx + 1):
            fqdn = "{}{}{}".format(host_prefix, idx, host_postfix)
            if not fqdn in model[DATA][ANSIBLE_NAME_BY_FQDN]:
                ERROR("For pool '{}': There is no node with fqdn like '{}'!".format(pool, fqdn))
            pool_desc[ANSIBLE_NAMES].append(model[DATA][ANSIBLE_NAME_BY_FQDN][fqdn])
        for idx in range(volume_first_idx, volume_last_idx + 1):
            pool_desc[VOLUMES].append("{}{}{}".format(volume_prefix, idx, volume_postfix))
        return pool_desc
        

   
def lookupMinioRepository(model, tenant):
    if REPOSITORIES not in model["config"] or MINIO not in model["config"][REPOSITORIES]:
        ERROR("Missing {}.{} in configuration file".format(REPOSITORIES, MINIO))
    l = filter(lambda x: x["repo_id"] == tenant[REPO_ID], model["config"][REPOSITORIES][MINIO])
    if len(l) > 1:
        ERROR("{} repo_id '{}' is defined twice in configuration file!".format(MINIO, tenant[REPO_ID]))
    if len(l) != 1:
        ERROR("{} repo_id '{}' is not defined in configuration file!".format(MINIO, tenant[REPO_ID]))
    tenant[REPOSITORY] = l[0]
        
        
def ensureTls(model, base):
    if (TLS_CRT in base) != (TLS_KEY in base):
        ERROR("tls_crt' and 'tls_key' must be both defined or any of them!") 
    if TLS_KEY in base:
        base[TLS_KEY] = appendPath(model[DATA][SOURCE_FILE_DIR], base[TLS_KEY])
        base[TLS_CRT] = appendPath(model[DATA][SOURCE_FILE_DIR], base[TLS_CRT])
        if not os.path.isfile(base[TLS_KEY]):
            ERROR("Unable to find '{}'".format(base[TLS_KEY]))
        if not os.path.isfile(base[TLS_CRT]):
            ERROR("Unable to find '{}'".format(base[TLS_CRT]))
            

def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER][MINIO], DISABLED, False)
    if model[CLUSTER][MINIO][DISABLED]:
        return False
    else:
        # need ansiblenameByFqdn
        model[DATA][ANSIBLE_NAME_BY_FQDN] = {}
        for node in model[CLUSTER][NODES]:
            model[DATA][ANSIBLE_NAME_BY_FQDN][node[FQDN]] = node[NAME]
        # Now, groom each tenant    
        for tenant in model[CLUSTER][MINIO][TENANTS]:
            setDefaultInMap(tenant, BIND_ADDRESS, "0.0.0.0")
            setDefaultInMap(tenant, BIND_PORT, 9000)
            setDefaultInMap(tenant, USER, "minio")
            setDefaultInMap(tenant, GROUP, "minio")
            lookupMinioRepository(model, tenant)
            tenant[POOL_EXTS] = []
            ensureTls(model, tenant)
            for pool in tenant[POOLS]:
                if (TLS_CRT in tenant) != (pool.startswith("https")):
                    ERROR("Pool must start with 'https' if (and only if) tls_crt is defined!")
                tenant[POOL_EXTS].append({ DEFINITION: pool, PARSED: parse_pool(model, pool)})
            if CONSOLE in tenant:
                setDefaultInMap(tenant[CONSOLE], BIND_ADDRESS, "0.0.0.0")
                setDefaultInMap(tenant[CONSOLE], BIND_PORT, 9090)
                setDefaultInMap(tenant[CONSOLE], TLS_BIND_PORT, 9443)
                ensureTls(model, tenant[CONSOLE])
                if TLS_CRT in tenant:
                    if SERVER_CA in tenant[CONSOLE]:
                        tenant[CONSOLE][SERVER_CA] = appendPath(model[DATA][SOURCE_FILE_DIR], tenant[CONSOLE][SERVER_CA])
                        if not os.path.isfile(tenant[CONSOLE][SERVER_CA]):
                            ERROR("Unable to find '{}'".format(tenant[CONSOLE][SERVER_CA]))
                    else:
                        ERROR("Tenant '{}' is configured for TLS. Console definition must include 'server_ca' parameter".format(tenant[NAME]))
        # Build the list of ansible node for each tenant
        for tenant in model[CLUSTER][MINIO][TENANTS]:
            nodeSet = Set()
            for poolExt in tenant[POOL_EXTS]:
                for node in poolExt[PARSED][ANSIBLE_NAMES]:
                    nodeSet.add(node)
            tenant[ANSIBLE_NAMES] = list(nodeSet)
        
        # Check there is no volume used twice on same node
        volumeSet = Set()
        for tenant in model[CLUSTER][MINIO][TENANTS]:
            for poolExt in tenant[POOL_EXTS]:
                for node in poolExt[PARSED][ANSIBLE_NAMES]:
                    for volume in poolExt[PARSED][VOLUMES]:
                        key = node + ":" + volume
                        if key in volumeSet:
                            ERROR("Volume '{}' is used twice on node '{}'".format(volume, node))
                        volumeSet.add(key)
        
        return True
    
    
    
    
    
    
    
    
    
