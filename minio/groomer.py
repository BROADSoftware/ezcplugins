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

from misc import setDefaultInMap,lookupRepository,ERROR
import re
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
            setDefaultInMap(tenant, USER, tenant[NAME])
            setDefaultInMap(tenant, GROUP, tenant[NAME])
            lookupMinioRepository(model, tenant)
            tenant[POOL_EXTS] = []
            for pool in tenant[POOLS]:
                tenant[POOL_EXTS].append({ DEFINITION: pool, PARSED: parse_pool(model, pool)})
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
    
    
    
    
    
    
    
    
    
