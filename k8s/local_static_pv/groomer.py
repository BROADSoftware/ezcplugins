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
import re
from sets import Set


CLUSTER = "cluster"
ROLES="roles"
K8S="k8s"
DATA_DISKS="data_disks"
COUNT="count"
SPLITS="splits"
SIZE="size"
HOST_DIR="host_dir"
STORAGE_CLASS="storage_class"
STORAGE_CLASSES="storage_classes"
SOURCES="sources"
FOLDER="folder"
NAME="name"
DATA_DISK_REF="data_disk_ref"
REF="ref"
TYPE="type"
LOCAL_STATIC_PVS="local_static_pvs"
PV_MOUNT_FOLDERS="pvMountFolders"

DATA="data"
ROLE_BY_NAME="roleByName"
DEVICE="device"
LVM_SPLITTERS="lvmSplitters"
BIND_MOUNTS="bindMounts"
LOCAL_STATIC_STORAGE_CLASSES="localStaticStorageClasses"

SC_TYPE_LOCAL_STATIC="local_static"

nameCheckRegex = re.compile('^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\\\\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$')


def isA_subdirOfB_orAisB(A, B):
    """It is assumed that A is a directory."""
    relative = os.path.relpath(os.path.realpath(A), os.path.realpath(B))
    return not (relative == os.pardir or  relative.startswith(os.pardir + os.sep))

def invalidSourceError(role, lpv, index):
    ERROR("role['{}'].k8s.local_static_pv.host_dir['{}'][{}]': A source must be defined with 'folder' and 'count' attribute OR 'data_disk_ref' and 'splits' attributes".format(role[NAME], lpv[HOST_DIR], index))

def groom(_plugin, model):
    # Lookup interesting storage classes
    localSaticStorageClassByName = {}
    model[DATA][LOCAL_STATIC_STORAGE_CLASSES] = []
    for sc in model[CLUSTER][K8S][STORAGE_CLASSES]:
        if nameCheckRegex.match(sc["name"]) is None:
            ERROR("Invalid storage_class name '{}': DNS-1123 subdomain must consist of lower case alphanumeric characters, '-' or '.', and must start and end with an alphanumeric character".format(sc["name"]))
        if sc[TYPE] == SC_TYPE_LOCAL_STATIC:
            localSaticStorageClassByName[sc[NAME]] = sc
            model[DATA][LOCAL_STATIC_STORAGE_CLASSES].append(sc)
    
    model[DATA][PV_MOUNT_FOLDERS] = []
    
    for _, role in model[DATA][ROLE_BY_NAME].items():
        # Lookup interesting raw dataDsisk
        dataDiskByRef = {}
        if DATA_DISKS in role:
            for ddisk in role[DATA_DISKS]:
                if REF in ddisk:
                    dataDiskByRef[ddisk[REF]] = ddisk
                    ddisk[SPLITS] = []

        
        storageClasses = Set()
        hostDirs = Set()
        role[LVM_SPLITTERS] = []
        role[BIND_MOUNTS] = []
        splitCount = 0
        if K8S in role and LOCAL_STATIC_PVS in role[K8S]:
            for lpv in role[K8S][LOCAL_STATIC_PVS]:
                if lpv[STORAGE_CLASS] not in localSaticStorageClassByName:
                    ERROR("role['{}'].k8s.local_static_pv.host_dir['{}']': Undefined storage_class '{}'".format(role[NAME], lpv[HOST_DIR], lpv[STORAGE_CLASS]))
                if lpv[STORAGE_CLASS] in storageClasses:
                    ERROR("role['{}'].k8s.local_static_pv: storage_class '{}' is used twice".format(role[NAME], lpv[STORAGE_CLASS]))
                storageClasses.add(lpv[STORAGE_CLASS])
                if lpv[HOST_DIR] in hostDirs:
                    ERROR("role['{}'].k8s.local_static_pv: host_dir '{}' is used twice".format(role[NAME], lpv[HOST_DIR]))
                hostDirs.add(lpv[HOST_DIR])
                    
                for index, source in enumerate(lpv[SOURCES]):
                    if FOLDER in source:
                        if DATA_DISK_REF in source or SPLITS in source or COUNT not in source:
                            invalidSourceError(role, lpv, index)
                        for _ in range(0, source[COUNT]):
                            mount = {}
                            role[BIND_MOUNTS].append(mount)
                            name = "vol{:03}".format(len(role[BIND_MOUNTS]))
                            mount["path"] = appendPath(lpv[HOST_DIR], name)
                            mount["src"] = appendPath(source[FOLDER], name)
                    elif DATA_DISK_REF in source:
                        if FOLDER in source or COUNT in source or SPLITS not in source:
                            invalidSourceError(role, lpv, index)
                        if source[DATA_DISK_REF] in dataDiskByRef:
                            ddisk = dataDiskByRef[source[DATA_DISK_REF]]
                            for size in source[SPLITS]:
                                split = {}
                                ddisk[SPLITS].append(split)
                                splitCount += 1
                                split[NAME] = "split{:03}".format(splitCount)
                                split["_size"] = size
                                split["mount"] = appendPath(lpv[HOST_DIR], split[NAME])
                        else:
                            ERROR("role['{}'].k8s.local_static_pv.host_dir['{}'][{}]': Undefined data_disk_ref '{}'".format(role[NAME], lpv[HOST_DIR], index, source[DATA_DISK_REF]))
                    else:      
                        invalidSourceError(role, lpv, index)
                pvMountFolder = {}
                pvMountFolder["className"] = lpv[STORAGE_CLASS]
                pvMountFolder["hostDir"] = lpv[HOST_DIR]
                model[DATA][PV_MOUNT_FOLDERS].append(pvMountFolder)
                
            # Now, loop on data_disk to build splitter
            for ref, ddisk in dataDiskByRef.items():
                if len(ddisk[SPLITS]) > 0:
                    requiredSize = 0
                    splitter = {}
                    role[LVM_SPLITTERS].append(splitter)
                    splitter["physical_volumes"] = [ "/dev/{}".format(ddisk[DEVICE]) ]
                    splitter["vg_name"] = "vg{}".format(ddisk[DEVICE]) 
                    splitter["logical_volumes"] = []
                    for split in ddisk[SPLITS]:
                        splitter["logical_volumes"].append(split)
                        split["size"] = "{}G".format(split["_size"])
                        split["fstype"] = "xfs"
                        split["mount_options"] = "defaults,noatime"
                        split["fsopts"] = ""
                        requiredSize += split["_size"]
                    if requiredSize > ddisk[SIZE]:
                        ERROR("role['{}'].data_disk.ref[{}]: Required size ({}G) exceed disk size ({}G)'".format(role[NAME], ref, requiredSize, ddisk[SIZE]))
    return True    

