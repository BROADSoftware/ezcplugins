# Copyright (C) 2021 BROADSoftware
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
import getpass
import copy
import re
import logging
from misc import ERROR, setDefaultInMap, appendPath


#TDISK_DEVICE_FROM_IDX= ["/dev/sdb", "/dev/sdc", "/dev/sdd", "/dev/sde", "/dev/sdf", "/dev/sdg", "/dev/sdh", "/dev/sdi"]
DISK_DEVICE_FROM_IDX= ["/dev/xvdb", "/dev/xvdc", "/dev/xvdd", "/dev/xvde", "/dev/xvdf", "/dev/xvdg", "/dev/xvdh", "/dev/xvdi"]


CLUSTER="cluster"
DATA="data"
CONFIG="config"
AWS="aws"
NAME="name"
INFRAS="infras"
INFRA="infra"
PROFILE_BY_USER="profile_by_user"
LOGIN="login"
PROFILE="profile"
DATA_DISK_BY_NODE="dataDiskByNode"
SUBNETS="subnets"
NODES="nodes"
TERRA_NAME="terraName"
SUBNET="subnet"
SUBNET_ALIASES="subnet_aliases"
ROLE_BY_NAME="roleByName"
ROLE="role"
TAGS="tags"
DATA_DISKS="data_disks"
FQDN="fqdn"
ID="id"
INDEX="index"
ALIAS="alias"
SECURITY_GROUP_BY_NAME="securityGroupByName"
SECURITY_GROUP="security_group"
# Added to cluster definition
SECURITY_GROUP_ID="security_group_id"
EXTERNAL_SECURITY_GROUPS="externalSecurityGroups"
DISK_TO_MOUNT_COUNT="disksToMountCount"
MOUNT="mount"
DEVICE_AWS="device_aws"
DEVICE_HOST="device_host"
DEVICE="device"
ROOT_TYPE="root_type"
TYPE="type"
NEED_MY_VPC="needMyVpc"
SECURITY_GROUPS="security_groups"
INBOUND_RULES="inbound_rules"
OUTBOUND_RULES="outbound_rules"
INGRESS="ingress"
EGRESS="egress"
SOURCE="source"
DESTINATION="destination"
FROM_PORT="from_port"
TO_PORT= "to_port"
PROTOCOL="protocol"
DESCRIPTION="description"
CIDR_BLOCK="cidr_block"
SELF="self"
ICMP_TYPE="icmp_type"
ICMP_CODE="icmp_code"
PORT="port"
KEY_PAIR="key_pair"
PRIVATE_KEY_PATH_BY_USER="private_key_path_by_user"
PRIVATE_KEY_PATH="privateKeyPath"
PATH="path"
AMAZON_MACHINE_IMAGES="amazon_machine_images"
AMI_BY_REGION="ami_by_region"
AMI_ID="ami_id"
REGION="region"
AMI="ami"
OWNER="owner"


logger = logging.getLogger("ezcluster.plugins.aws")


def terraName(n):
    return n.replace('.', "_")


def list_to_map(list, key):
    m = {}
    for x in list:
        m[x[key]] = x
    return m


def addTags(root, newTags):
    if not TAGS in root:
        root[TAGS] = {}
    for k, v in newTags.iteritems():
        if k not in root[TAGS]:
            root[TAGS][k] = v


def number_or_none(strg):
    if strg != None:
        try:
            return int(strg)
        except ValueError:
            return None
    return None


ICMP_TYPE_FROM_STRING = {
    "echo-reply": 0,
    "echo-request": 8
}


def handle_icmp_type(rule, prefix):
    if PORT in rule or FROM_PORT in rule or TO_PORT in rule:
        ERROR("{}: There should be no port definition when using ICMP".format(prefix))
    if ICMP_TYPE not in rule:
        ERROR("{}: 'icmp_type' is mandatory when protocol == 'ICMP'".format(prefix))
    if ICMP_CODE in rule:
        code = rule[ICMP_CODE]
    else:
        code = 0
    itype = number_or_none(rule[ICMP_TYPE])
    if itype is None:
        t = rule[ICMP_TYPE].strip().lower()
        if t in ICMP_TYPE_FROM_STRING:
            return ICMP_TYPE_FROM_STRING[t], code
        else:
            ERROR("{}: Unknown 'icmp_type' value: {}".format(prefix, rule[ICMP_TYPE]))
    else:
        return itype, code


PORT_FROM_STRING = {
    "ftp-data": 20,
    "ftp": 21,
    "ssh": 22,
    "telnet": 23,
    "smtp": 25,
    "tftp": 69,
    "http": 80,
    "pop3": 110,
    "sftp": 115,
    "ntp": 123,
    "imap3": 220,
    "https": 443
}


# Return ( <fromPort>, <toPort> )
def handle_tcp_udp_port(rule, prefix):
    if PORT in rule:
        if FROM_PORT in rule or TO_PORT in rule:
            ERROR("{}: 'port' and ('from_port', 'to_port') can't be used together".format(prefix))
        x = number_or_none(rule[PORT])
        if x is None:
            return x, x
        else:
            p = rule[PORT].strip().lower()
            if p in PORT_FROM_STRING:
                return PORT_FROM_STRING[p], PORT_FROM_STRING[p]
            else:
                ERROR("{}: Unknown port name '{}'".format(prefix, rule[PORT]))
    else:
        if FROM_PORT not in rule or TO_PORT not in rule:
            ERROR("{}: 'from_port' and 'to_port' must be both defined if 'port' is not".format(prefix))
        return rule[FROM_PORT], rule[TO_PORT]


cidrCheck = re.compile("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}$")


def is_cidr(peer):
    if not peer[0].isdigit():
        return False
    else:
        if not cidrCheck.match(peer):
            ERROR("Invalid source/destination '{}'. Not a valid CIDR".format(peer))
        return True


def compute_security_group_rule(model, rule, sgName, ruleIdx):
    tf = {}
    if DESCRIPTION in rule:
        tf[DESCRIPTION] = rule[DESCRIPTION]
    prefix = "security_group[{}]  Rule#{}".format(sgName, ruleIdx)
    # Handle protocol
    proto = rule[PROTOCOL].strip().upper()
    tf[PROTOCOL] = proto
    p = number_or_none(proto)
    if p != None:
        # Protocol specified by number. No other control
        tf[FROM_PORT] = rule[FROM_PORT]
        tf[TO_PORT] = rule[TO_PORT]
    elif proto == "ALL":
        tf[FROM_PORT] = 0
        tf[TO_PORT] = 0
        tf[PROTOCOL] = "-1"
    elif proto == "TCP" or proto == "UDP":
        (tf[FROM_PORT], tf[TO_PORT]) = handle_tcp_udp_port(rule, prefix)
    elif rule[PROTOCOL].upper() == "ICMP":
        (tf[FROM_PORT], tf[TO_PORT]) = handle_icmp_type(rule, prefix)
    else:
        ERROR("{}: Unknow protocol token:'{}'".format(prefix, rule[PROTOCOL]))
    # Handle source or destination
    if SOURCE in rule:
        peer = rule[SOURCE].strip()
    else:
        peer = rule[DESTINATION].strip()
    if peer.upper() == "_ANY_":
        tf[CIDR_BLOCK] = "0.0.0.0/0"
    elif peer.upper() == "_SELF_":
        tf[SELF] = True
    elif peer.upper() == "_VPC_":
        tf[CIDR_BLOCK] = "${data.aws_vpc.my_vpc.cidr_block}"
        model[DATA][AWS][NEED_MY_VPC] = True
    elif is_cidr(peer):
        tf[CIDR_BLOCK] = peer
    else:
        if peer == sgName:
            # This refers to ourself
            tf[SELF] = True
        elif peer in model[DATA][AWS][SECURITY_GROUP_BY_NAME]:
            # Should be a reference to another SG.
            tf[SECURITY_GROUP] = "aws_security_group." + peer + ".id"
        else:
            model[DATA][AWS][EXTERNAL_SECURITY_GROUPS].add(peer)
            tf[SECURITY_GROUP] = "data.aws_security_group." + peer + ".id"
    return tf


def groom_security_groups(model):
    model[DATA][AWS][EXTERNAL_SECURITY_GROUPS] = set()
    model[DATA][AWS][SECURITY_GROUP_BY_NAME] = {}
    model[DATA][AWS][NEED_MY_VPC] = False
    if SECURITY_GROUPS in model[CLUSTER][AWS]:
        # First, a loop to find all our defined SG
        for sg in model[CLUSTER][AWS][SECURITY_GROUPS]:
            model[DATA][AWS][SECURITY_GROUP_BY_NAME][sg[NAME]] = sg
        # Now, loop again to groom
        for sg in model[CLUSTER][AWS][SECURITY_GROUPS]:
            sg[INGRESS] = []
            for idx, inbound in enumerate(sg[INBOUND_RULES]):
                sg[INGRESS].append(compute_security_group_rule(model, inbound, sg[NAME], idx))
            sg[EGRESS] = []
            for idx, outbound in enumerate(sg[OUTBOUND_RULES]):
                sg[EGRESS].append(compute_security_group_rule(model, outbound, sg[NAME], idx))
            addTags(sg, {"Name": sg[NAME], "Cluster": model[CLUSTER][ID], "Owner": model[CLUSTER][AWS][OWNER]})


def groom_roles(model):
    for roleName, role in model[DATA][ROLE_BY_NAME].iteritems():
        if role[AWS][SECURITY_GROUP] in model[DATA][AWS][SECURITY_GROUP_BY_NAME]:
            role[AWS][SECURITY_GROUP_ID] = "aws_security_group." + role[AWS][SECURITY_GROUP] + ".id"
        else:
            model[DATA][AWS][EXTERNAL_SECURITY_GROUPS].add(role[AWS][SECURITY_GROUP])
            role[AWS][SECURITY_GROUP_ID] = "data.aws_security_group." + role[AWS][SECURITY_GROUP] + ".id"
        if AMI in role[AWS]:
            role[AWS][AMI] = get_ami(model[CONFIG], role[AWS][AMI], model[DATA][AWS][INFRA][REGION])
        elif AMI in model[DATA][AWS][INFRA]:
            role[AWS][AMI] = model[DATA][AWS][INFRA][AMI]
        else:
            ERROR("No 'ami' defined for role '{}' and in global scope".format(roleName))
        setDefaultInMap(role[AWS], ROOT_TYPE, "gp2")
        role[DISK_TO_MOUNT_COUNT] = 0
        if DATA_DISKS in role:
            for i in range(0, len(role[DATA_DISKS])):
                role[DATA_DISKS][i][INDEX] = i
                setDefaultInMap(role[DATA_DISKS][i], DEVICE, DISK_DEVICE_FROM_IDX[i])
                setDefaultInMap(role[DATA_DISKS][i], DEVICE_AWS, role[DATA_DISKS][i][DEVICE])
                setDefaultInMap(role[DATA_DISKS][i], DEVICE_HOST, role[DATA_DISKS][i][DEVICE])
                if MOUNT in role[DATA_DISKS][i]:
                    role[DISK_TO_MOUNT_COUNT] += 1
                setDefaultInMap(role[DATA_DISKS][i], TYPE, "gp2")


# WARNING: Loop for data disks must occurs on the same node array here and in the main.tf template
def groom_nodes(model):
    # model[DATA][AWS][DATA_DATA_DISKS] = []
    model[DATA][AWS][DATA_DISK_BY_NODE] = {}
    model[DATA][AWS][SUBNETS] = []
    subnets = set()
    subnetByAlias = list_to_map(model[DATA][AWS][INFRA][SUBNET_ALIASES], ALIAS)
    for node in model[CLUSTER][NODES]:
        node[TERRA_NAME] = terraName(node[NAME])
        if node[AWS][SUBNET] in subnetByAlias:
            node[AWS][SUBNET] = subnetByAlias[node[AWS][SUBNET]][NAME]
        # Replace subnet by a map name, terraName
        subnet = {NAME: node[AWS][SUBNET], TERRA_NAME: terraName(node[AWS][SUBNET])}
        node[AWS][SUBNET] = subnet
        if subnet[NAME] not in subnets:
            subnets.add(subnet[NAME])
            model[DATA][AWS][SUBNETS].append(subnet)
        role = model[DATA][ROLE_BY_NAME][node[ROLE]]
        if TAGS in role[AWS]:
            addTags(node[AWS], role[AWS][TAGS])
        addTags(node[AWS], {"Name": node[FQDN], "Cluster": model[CLUSTER][ID], "Owner": model[CLUSTER][AWS][OWNER]})
        # Handle dataDisks
        if DATA_DISKS in role and len(role[DATA_DISKS]) > 0:
            dataDisks = copy.deepcopy(role[DATA_DISKS])
            for d in dataDisks:
                d[TERRA_NAME] = "{}_{}".format(node[TERRA_NAME], d[INDEX])
            model[DATA][AWS][DATA_DISK_BY_NODE][node[NAME]] = dataDisks


def lookup_infra(model, infraName):
    for infra in model[CONFIG][INFRAS]:
        if infra[NAME] == infraName:
            return infra
    ERROR("Unable to find an infra names '{}' in configuration".format(infraName))


def fix_profile(infra):
    login = getpass.getuser()
    for p in infra[PROFILE_BY_USER]:
        if p[LOGIN] == login:
            infra[PROFILE] = p[PROFILE]
            return
    ERROR("Unable to find a profile for user '{}' in infra '{}'".format(login, infra[NAME]))


def fix_key_pair(model, infra):
    login = getpass.getuser()
    for pkp in infra[KEY_PAIR][PRIVATE_KEY_PATH_BY_USER]:
        if pkp[LOGIN] == login:
            infra[KEY_PAIR][PRIVATE_KEY_PATH] = pkp[PATH]
            # If path is relative, adjust to config file location
            infra[KEY_PAIR][PRIVATE_KEY_PATH] = appendPath(os.path.dirname(model["data"]["configFile"]), infra[KEY_PAIR][PRIVATE_KEY_PATH])
            return
    logger.warning("Unable to find a private_key_path for user '{}' in infra '{}'. Will use default key".format(login, infra[NAME]))

SSH_USER="ssh_user"

def get_ami(config, os, region):
    ami = {}
    for x in config[AMAZON_MACHINE_IMAGES]:
        if x[NAME] == os:
            ami[SSH_USER] = x[SSH_USER]
            for y in x[AMI_BY_REGION]:
                if y[REGION] == region:
                    ami[ID] = y[AMI_ID]
                    return ami
            ERROR("Unable to find an AMI for region='{}' for os='{}' in configuration".format(region, os))
    ERROR("Unable to find AMI list for os='{}' in configuration".format(os))


def groom(_plugin, model):
    model[DATA][AWS] = {}
    model[DATA][AWS][INFRA] = infra = lookup_infra(model, model[CLUSTER][AWS][INFRA])
    fix_profile(infra)
    fix_key_pair(model, infra)
    if AMI in model[CLUSTER][AWS]:  # If not, must be defined in the role
        infra[AMI] = get_ami(model[CONFIG], model[CLUSTER][AWS][AMI], infra[REGION])
    groom_security_groups(model)
    groom_roles(model)
    groom_nodes(model)
    model["data"]["buildScript"] = appendPath(model["data"]["targetFolder"], "build.sh")
    return True     # Always enabled

