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

from misc import setDefaultInMap,ERROR
from collections import Mapping
import copy
import ipaddress
from sets import Set

CLUSTER = "cluster"
K8S="k8s"
DISABLED = "disabled"
CLUSTERS="clusters"
ROOK_CEPH="rook_ceph"
DATA="data"
CLUSTER_BY_NAME="clusterByName"
STORAGE="storage"
GROUP="group"
GROUP_BY_NAME="groupByName"
NODE_CONFIGS="node_configs"
NAME="name"
NODES="nodes"
BLOCK_POOLS="block_pools"
REPLICATION="replication"
DASHBOARD_IP="dashboard_ip"
METALLB="metallb"
EXTERNAL_IP_RANGE="external_ip_range"
FIRST="first"
LAST="last"
DEVICES="devices"
GROUPS_WITH_DEVICES="groupsWithDevices"

def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER], K8S, {})
    setDefaultInMap(model[CLUSTER][K8S], ROOK_CEPH, {})
    setDefaultInMap(model[CLUSTER][K8S][ROOK_CEPH], DISABLED, False)
    if model[CLUSTER][K8S][ROOK_CEPH][DISABLED]:
        return False
    else:
        setDefaultInMap(model[CLUSTER][K8S][ROOK_CEPH], CLUSTERS, [])
        setDefaultInMap(model[DATA], K8S, {})
        setDefaultInMap(model[DATA][K8S], ROOK_CEPH, {})
        setDefaultInMap(model[DATA][K8S][ROOK_CEPH], CLUSTER_BY_NAME, {})
        groupsWithDevice = Set()
        model[DATA][K8S][ROOK_CEPH][GROUPS_WITH_DEVICES] = groupsWithDevice
        for cluster in model[CLUSTER][K8S][ROOK_CEPH][CLUSTERS]:
            dataCluster = {}
            nodeByName = {}
            for config in cluster[NODE_CONFIGS]:
                if not isinstance(config, Mapping):
                    ERROR("rook_ceph.clusters.['{}']: All node_configs items must be a Map".format(cluster[NAME]))
                if not GROUP in config:
                    ERROR("rook_ceph.clusters.['{}']: All node_configs items must have a 'group' attribute".format(cluster[NAME]))
                if not config[GROUP] in model[DATA][GROUP_BY_NAME]:
                    ERROR("rook_ceph.clusters.{}.node_configs: group '{}' does not exists".format(cluster["name"], config[GROUP]))
                for nodeName in model[DATA][GROUP_BY_NAME][config[GROUP]]:
                    if nodeName in nodeByName:
                        ERROR("rook_ceph.clusters.['{}'].node_configs: node '{}' belong to both group '{}' and group '{}'. nodes_config.groups can't overlap in the same cluster!".format(cluster[NAME], nodeName, config[GROUP], nodeByName[nodeName][GROUP]))
                    nodeByName[nodeName] = copy.deepcopy(config)
                if DEVICES in config:
                    groupsWithDevice.add(config[GROUP])
            dataCluster[NODES] = []
            for nodeName, node in nodeByName.iteritems():
                node = nodeByName[nodeName]
                del(node[GROUP])
                node[NAME] = nodeName
                dataCluster[NODES].append(node)
            model[DATA][K8S][ROOK_CEPH][CLUSTER_BY_NAME][cluster["name"]] = dataCluster
            if BLOCK_POOLS in cluster:
                for bp in cluster[BLOCK_POOLS]:
                    if NAME not in bp:
                        bp[NAME] = "{}_bp_{}".format(cluster[NAME], bp[REPLICATION])
            if DASHBOARD_IP in cluster:
                if not METALLB in model[CLUSTER][K8S]:
                    ERROR("rook_ceph.clusters.{}.dashboard_ip is defined while there is no metallb defined".format(cluster["name"]))
                db_ip =  ipaddress.ip_address(u"" + cluster[DASHBOARD_IP])
                first_ip = ipaddress.ip_address(u"" + model[CLUSTER][K8S][METALLB][EXTERNAL_IP_RANGE][FIRST])
                last_ip = ipaddress.ip_address(u"" + model[CLUSTER][K8S][METALLB][EXTERNAL_IP_RANGE][LAST])
                if db_ip < first_ip or db_ip > last_ip:
                    ERROR("rook_ceph.clusters.{}.dashboard_ip is not included in metallb.external_ip_range".format(cluster["name"]))
        return True
