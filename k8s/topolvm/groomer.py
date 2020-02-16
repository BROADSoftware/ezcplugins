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

from misc import setDefaultInMap,lookupRepository
from sets import Set
from jinja2._compat import iteritems
 
CLUSTER = "cluster"
K8S="k8s"
DATA="data"
TOPOLVM="topolvm"
DISABLED = "disabled"
REPO_ID="repo_id"
ROLE_BY_NAME="roleByName"
DATA_DISKS="data_disks"
DATA_DISK_REF="data_disk_ref"
REF="ref"
DEVICES_BY_NODES="deviceByNode"
NODES="nodes"
DEVICE="device"
GROUP="group"
SIZE_BY_NODE="sizeByNode"
SIZE="size"
FSTYPE="fstype"
SPARE_SIZE="spare_size"
STORAGE_CLASS="storage_class"

def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER][K8S][TOPOLVM], DISABLED, False)
    setDefaultInMap(model[DATA], K8S, {})
    setDefaultInMap(model[DATA][K8S],TOPOLVM, {})
    if model[CLUSTER][K8S][TOPOLVM][DISABLED]:
        return False
    else:
        setDefaultInMap(model[CLUSTER][K8S][TOPOLVM], FSTYPE, "xfs")
        setDefaultInMap(model[CLUSTER][K8S][TOPOLVM], SPARE_SIZE, 10)
        setDefaultInMap(model[CLUSTER][K8S][TOPOLVM], STORAGE_CLASS, "topolvm")
        lookupRepository(model, None, "topolvm", model[CLUSTER][K8S][TOPOLVM][REPO_ID])
        setDefaultInMap(model[DATA][K8S][TOPOLVM], DEVICES_BY_NODES, {})
        setDefaultInMap(model[DATA][K8S][TOPOLVM], SIZE_BY_NODE, {})
        setDefaultInMap(model[DATA][K8S][TOPOLVM], GROUP, Set())
        topolvmRef = model[CLUSTER][K8S][TOPOLVM][DATA_DISK_REF]
        for _, role in iteritems(model[DATA][ROLE_BY_NAME]):
            if DATA_DISKS in role:
                for disk in role[DATA_DISKS]:
                    if REF in disk and disk[REF] == topolvmRef:
                        for node in role[NODES]:
                            setDefaultInMap(model[DATA][K8S][TOPOLVM][DEVICES_BY_NODES], node, [])
                            setDefaultInMap(model[DATA][K8S][TOPOLVM][SIZE_BY_NODE], node, 0)
                            model[DATA][K8S][TOPOLVM][DEVICES_BY_NODES][node].append("/dev/" + disk[DEVICE])
                            model[DATA][K8S][TOPOLVM][SIZE_BY_NODE][node] += disk[SIZE]
                            model[DATA][K8S][TOPOLVM][GROUP].add(node)
        print "------- TOPOLVM Node capacity:"
        for node, size in iteritems(model[DATA][K8S][TOPOLVM][SIZE_BY_NODE]):
            print "\t{} -> {}GB".format(node, size)
        return True
