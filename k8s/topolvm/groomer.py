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
from sets import Set
import copy

CLUSTER = "cluster"
K8S="k8s"
DATA="data"
TOPOLVM="topolvm"
DISABLED = "disabled"
REPO_ID="repo_id"
SPARE_GB="spare_gb"
STORAGE_CLASS="storage_class"
VOLUME_GROUP="volume_group"
FSTYPE="fstype"
NAME="name"
DEVICE_CLASSES = "device_classes"
VOLUME_GROUP_BY_NODE="volumeGroupsByNode"
DEVICE_CLASSES_BY_NODE="deviceClassesByNode" 
TOPOLVM_DEVICE_CLASS="topolvm_device_class"
DATA_DISKS="data_disks"
LVMD_HOSTS="lvmdHosts"
ROLE_BY_NAME="roleByName"
SIZE="size"
PHYSICAL_VOLUMES="physical_volumes"
DEVICE="device"
NODE_BY_NAME="nodeByName"
NODES="nodes"
ALLOW_VOLUME_EXPANSION="allow_volume_expansion"

"""
In model[DATA][K8S][TOPOLVM]:

deviceClassesByNode:
  node1:
  - name: ...
    storage_class: ...
    volume_group: ...
    fstype: ...
    spare_gb: ...
  - name: ...
    storage_class: ...
    volume_group: ...
    fstype: ...
    spare_gb: ...
  node2:
    ...
  
volumeGroupsByNode:
  node1:
  - name: ...
    physicalVolumes:
    - device1
    - device2
  node2:
    ....
"""


def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER][K8S][TOPOLVM], DISABLED, False)
    setDefaultInMap(model[DATA], K8S, {})
    setDefaultInMap(model[DATA][K8S],TOPOLVM, {})
    if model[CLUSTER][K8S][TOPOLVM][DISABLED]:
        return False
    else:
        deviceClassByName = {}
        for deviceClass in model[CLUSTER][K8S][TOPOLVM][DEVICE_CLASSES]:
            setDefaultInMap(deviceClass, SPARE_GB, 10)
            setDefaultInMap (deviceClass, STORAGE_CLASS, "topolvm-{}".format(deviceClass[NAME]))
            setDefaultInMap (deviceClass, VOLUME_GROUP, "topolvm-{}".format(deviceClass[NAME]))
            setDefaultInMap(deviceClass, FSTYPE, "xfs")
            setDefaultInMap(deviceClass, ALLOW_VOLUME_EXPANSION, False)
            deviceClassByName[deviceClass[NAME]] = deviceClass
        
        lookupRepository(model, None, "topolvm", model[CLUSTER][K8S][TOPOLVM][REPO_ID])
        
        model[DATA][K8S][TOPOLVM][VOLUME_GROUP_BY_NODE] = {}
        model[DATA][K8S][TOPOLVM][DEVICE_CLASSES_BY_NODE] = {}
        model[DATA][K8S][TOPOLVM][LVMD_HOSTS] = Set()
        
        for _, role in model[DATA][ROLE_BY_NAME].iteritems():
            deviceClassNames = Set()
            volumeGroupByName = {}
            if DATA_DISKS in role:
                for disk in role[DATA_DISKS]:
                    if TOPOLVM_DEVICE_CLASS in disk:
                        if disk[TOPOLVM_DEVICE_CLASS] not in deviceClassByName:
                            ERROR("Unknown device_class {} in role {}".format(disk[TOPOLVM_DEVICE_CLASS], role[NAME]))
                        dc = deviceClassByName[disk[TOPOLVM_DEVICE_CLASS]]
                        deviceClassNames.add(dc[NAME])
                        vgName = dc[VOLUME_GROUP]
                        setDefaultInMap(volumeGroupByName, vgName, { NAME: vgName, PHYSICAL_VOLUMES: [], SIZE: 0 })
                        vg = volumeGroupByName[vgName]
                        vg[PHYSICAL_VOLUMES].append("/dev/" + disk[DEVICE])
                        vg[SIZE] += disk[SIZE]
            if len(deviceClassNames) > 0:
                devicesClasses = []
                for dcName in deviceClassNames:
                    dc = copy.deepcopy(deviceClassByName[dcName])       # Need a deepcopy as default may be different
                    dc["default"] = (len(devicesClasses) == 0)          # Currently, topolvm need a default, or error
                    devicesClasses.append(dc)
                volumeGroups = list(volumeGroupByName.values())
                for nodeName in role[NODES]:
                    model[DATA][K8S][TOPOLVM][DEVICE_CLASSES_BY_NODE][nodeName] = devicesClasses
                    model[DATA][K8S][TOPOLVM][VOLUME_GROUP_BY_NODE][nodeName] = volumeGroups
                    model[DATA][K8S][TOPOLVM][LVMD_HOSTS].add(nodeName)
        print "------- TOPOLVM Node capacity:"
        for nodeName in model[DATA][NODE_BY_NAME].keys():
            if nodeName in model[DATA][K8S][TOPOLVM][VOLUME_GROUP_BY_NODE]:
                for vg in model[DATA][K8S][TOPOLVM][VOLUME_GROUP_BY_NODE][nodeName]:
                    print "\t{}:{} -> {}GB".format(nodeName, vg[NAME], vg[SIZE])
        return True
