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

from misc import ERROR,appendPath
import os
from sets import Set
import re


CLUSTER = "cluster"
ROLES="roles"
K8S="k8s"
DATA_DISKS="data_disks"
PERSISTENT_VOLUMES="persistent_volumes"
COUNT="count"
SPLITS="splits"
MOUNT="mount"
SIZE="size"
HOST_DIR="host_dir"
LOCAL_PERSISTENT_VOLUMES="local_persistent_volumes"
STORAGE_CLASSES="storage_classes"
STORAGE_CLASS="storage_class"

DATA="data"
ROLE_BY_NAME="roleByName"
DEVICE="device"
LVM_SPLITTERS="lvmSplitters"
BIND_MOUNTS="bindMounts"

nameCheckRegex = re.compile('^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\\\\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$')


def isA_subdirOfB_orAisB(A, B):
    """It is assumed that A is a directory."""
    relative = os.path.relpath(os.path.realpath(A), os.path.realpath(B))
    return not (relative == os.pardir or  relative.startswith(os.pardir + os.sep))


def groom(_plugin, model):
    # A first loop to check user input
    storageClasses = Set()
    
    for sc in model[CLUSTER][K8S][LOCAL_PERSISTENT_VOLUMES][STORAGE_CLASSES]:
        if nameCheckRegex.match(sc["name"]) is None:
            ERROR("Invalid storage_class name '{}': DNS-1123 subdomain must consist of lower case alphanumeric characters, '-' or '.', and must start and end with an alphanumeric character".format(sc["name"]))
        storageClasses.add(sc["name"])
    
    for role in model[CLUSTER][ROLES]:
        if DATA_DISKS in role:
            for disk in role[DATA_DISKS]:
                if K8S in disk and PERSISTENT_VOLUMES in disk[K8S]:
                    pv = disk[K8S][PERSISTENT_VOLUMES]
                    if COUNT in pv and SPLITS in pv:
                        ERROR("Both 'count' and 'splits' are defined on a persistent volume {}!".format(pv[HOST_DIR]))
                    if pv[STORAGE_CLASS] not in storageClasses:
                        ERROR("Persistent_volumes.host_dir='{}': undefined storage_class '{}'".format(pv[HOST_DIR], pv[STORAGE_CLASS]))
                    if SPLITS in pv:
                        dsum = 0
                        for split in pv[SPLITS]:
                            dsum += split
                        if dsum > disk[SIZE]:
                            ERROR("Persistent_volumes.host_dir='{}': Sum of splits ({}) exceed disk size ({})".format(pv[HOST_DIR], dsum, disk[SIZE]))
                        if MOUNT in disk:
                            ERROR("Persistent_volumes.host_dir='{}': For persistent_volumes defined by 'splits', the 'data_disk.mount' attribute must not be set.".format(pv[HOST_DIR]))
                    if COUNT in pv:
                        if MOUNT not in disk:
                            ERROR("Persistent_volumes.host_dir='{}': For persistent_volumes defined by 'count', the 'data_disk.mount' attribute must be set (Can be set to same values as host_dir).".format(pv[HOST_DIR]))
                        if isA_subdirOfB_orAisB(pv[HOST_DIR], disk[MOUNT]):
                            ERROR("Persistent_volumes.host_dir='{}' can't be same or a subfolder of disk.mount:{}".format(pv[HOST_DIR], disk[MOUNT]) )
                                                
                        
                        
    # Another loop to build splitters stuff
    for _, role in model[DATA][ROLE_BY_NAME].items():
        role[LVM_SPLITTERS] = []
        role[BIND_MOUNTS] = []
        if DATA_DISKS in role:
            for disk in role[DATA_DISKS]:
                if K8S in disk and PERSISTENT_VOLUMES in disk[K8S]:
                    pv = disk[K8S][PERSISTENT_VOLUMES]
                    if SPLITS in pv:
                        splitter = {}
                        role[LVM_SPLITTERS].append(splitter)
                        splitter["physical_volumes"] = [ "/dev/{}".format(disk[DEVICE]) ]
                        splitter["vg_name"] = "vg{}".format(disk[DEVICE]) 
                        splitter["logical_volumes"] = []
                        for idx, size in enumerate(pv[SPLITS]):
                            split = {}
                            splitter["logical_volumes"].append(split)
                            split["size"] = "{}G".format(size)
                            split["name"] = "split{:02}".format(idx + 1)
                            split["fstype"] = "xfs"
                            split["mount_options"] = "defaults,noatime"
                            split["fsopts"] = ""
                            split["mount"] = appendPath(pv[HOST_DIR],  split["name"])
                    if COUNT in pv:
                        for idx in range(0, pv[COUNT]):
                            mount = {}
                            role[BIND_MOUNTS].append(mount)
                            name = "vol{:02}".format(idx + 1)
                            mount["path"] = appendPath(pv[HOST_DIR], name)
                            mount["src"] = appendPath(disk[MOUNT], name)
                        
    return True
