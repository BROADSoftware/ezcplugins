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

from sets import Set
import re

from misc import ERROR,appendPath, setDefaultInMap

CLUSTER="cluster"
DATA="data"
CONFIG="config"
AWS="aws"

# In cluster definition
SUBNET="subnet"
NODES="nodes"
SECURITY_GROUPS="security_groups"
NAME="name"
INBOUND_RULES="inbound_rules"
OUTBOUND_RULES="outbound_rules"
SOURCE="source"
DESTINATION="destination"
FROM_PORT="from_port"
TO_PORT= "to_port"
PORT="port"
ICMP_TYPE="icmp_type"
ICMP_CODE="icmp_code"
PROTOCOL="protocol"
DESCRIPTION="description"
SECURITY_GROUP="security_group"
# Added to cluster definition
SECURITY_GROUP_ID="security_group_id"
ROOT_VOLUME_TYPE="root_volume_type"
ROLES="roles"     
KEY_PAIR="key_pair"

# In config definition
AWS_KEY_PAIRS="aws_key_pairs"
KEY_PAIR_ID="key_pair_id"
KEY_PAIR_NAME="key_pair_name"
PRIVATE_KEY_PATH="private_key_path"

# In data part
REFERENCE_SUBNET="referenceSubnet"
EXTERNAL_SECURITY_GROUPS="externalSecurityGroups"
SECURITY_GROUP_BY_NAME="securityGroupByName"
NEED_MY_VPC="needMyVpc"
ROLE_BY_NAME="roleByName"
KEY_PAIR_BY_ID="keyPairById"
DATA_KEY_PAIR="keyPair"

# In terraform layout
INGRESS="ingress"
EGRESS="egress"
CIDR_BLOCK="cidr_block"
SELF="self"

cidrCheck = re.compile("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}$")
#cidrCheck = re.compile("^.*$")

def isCidr(peer):
    if not peer[0].isdigit():
        return False
    else:
        if not cidrCheck.match(peer):
            ERROR("Invalid source/destination '{}'. Not a valid CIDR".format(peer))
        return True

def numberOrNone(strg):
    if strg != None:
        try:
            return int(strg)
        except ValueError:
            return None
    return None

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
def handleTcpUdpPort(rule, prefix):
    if PORT in rule:
        if FROM_PORT in rule or TO_PORT in rule:
            ERROR("{}: 'port' and ('from_port', 'to_port') can't be used together".format(prefix))
        x = numberOrNone(rule[PORT])
        if x != None:
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

ICMP_TYPE_FROM_STRING = {
    "echo-reply": 0,
    "echo-request": 8
}

def handleIcmpType(rule, prefix):
    if PORT in rule or FROM_PORT in rule or TO_PORT in rule:
        ERROR("{}: There should be no port definition when using ICMP".format(prefix))
    if ICMP_TYPE not in rule:
        ERROR("{}: 'icmp_type' is mandatory when protocol == 'ICMP'".format(prefix))
    if ICMP_CODE in rule:
        code = rule[ICMP_CODE]
    else:
        code = 0
    itype = numberOrNone(rule[ICMP_TYPE])
    if itype is None:
        t = rule[ICMP_TYPE].strip().lower()
        if t in ICMP_TYPE_FROM_STRING:
            return ICMP_TYPE_FROM_STRING[t], code
        else:
            ERROR("{}: Unknown 'icmp_type' value: {}".format(prefix, rule[ICMP_TYPE]))
    else:
        return itype, code
        
def computeTfSecurityGroupRule(model, rule, sgName, ruleIdx):
    tf = { }
    if DESCRIPTION in rule:
        tf[DESCRIPTION] = rule[DESCRIPTION]
    prefix = "security_group[{}]  Rule#{}".format(sgName, ruleIdx)
    # Handle protocol
    proto = rule[PROTOCOL].strip().upper()
    tf[PROTOCOL] = proto
    p = numberOrNone(proto)
    if p != None:
        # Protocol specified by number. No other control
        tf[FROM_PORT] = rule[FROM_PORT]
        tf[TO_PORT] = rule[TO_PORT]
    elif proto == "ALL":
        tf[FROM_PORT] = 0
        tf[TO_PORT] = 0
        tf[PROTOCOL] = "-1"
    elif proto == "TCP" or proto == "UDP":
        (tf[FROM_PORT], tf[TO_PORT]) = handleTcpUdpPort(rule, prefix)
    elif rule[PROTOCOL].upper() == "ICMP":
        (tf[FROM_PORT], tf[TO_PORT]) = handleIcmpType(rule, prefix)
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
        model[DATA][NEED_MY_VPC] = True
    elif isCidr(peer):
        tf[CIDR_BLOCK] = peer
    else:
        if peer == sgName:
            # This refers to ourself
            tf[SELF] = True
        elif peer in model[DATA][SECURITY_GROUP_BY_NAME]:
            # Should be a reference to another SG.
            tf[SECURITY_GROUP] = "aws_security_group." + peer + ".id"
        else:
            model[DATA][EXTERNAL_SECURITY_GROUPS].add(peer)
            tf[SECURITY_GROUP] = "data.aws_security_group." + peer + ".id"
    
    return tf
        
def groomSecurityGroups(model):
    model[DATA][EXTERNAL_SECURITY_GROUPS] = Set()
    model[DATA][SECURITY_GROUP_BY_NAME] = {}
    model[DATA][NEED_MY_VPC] = False
    # First, a loop to find all our defined SG
    if SECURITY_GROUPS in model[CLUSTER][AWS]:
        for sg in model[CLUSTER][AWS][SECURITY_GROUPS]:
            model[DATA][SECURITY_GROUP_BY_NAME][sg[NAME]] = sg
        # Now, loop again to find all external (Should be pre-existing)
        for sg in model[CLUSTER][AWS][SECURITY_GROUPS]:
            sg[INGRESS] = []
            for idx, inbound in enumerate(sg[INBOUND_RULES]):
                sg[INGRESS].append(computeTfSecurityGroupRule(model, inbound, sg[NAME], idx))
            sg[EGRESS] = []
            for idx, outbound in enumerate(sg[OUTBOUND_RULES]):
                sg[EGRESS].append(computeTfSecurityGroupRule(model, outbound, sg[NAME], idx))
            
def groomRoles(model):
    for _, role in model[DATA][ROLE_BY_NAME].iteritems():
        if role[AWS][SECURITY_GROUP] in model[DATA][SECURITY_GROUP_BY_NAME]:
            role[AWS][SECURITY_GROUP_ID] = "aws_security_group." + role[AWS][SECURITY_GROUP] + ".id"
        else:
            model[DATA][EXTERNAL_SECURITY_GROUPS].add(role[AWS][SECURITY_GROUP])
            role[AWS][SECURITY_GROUP_ID] = "data.aws_security_group." + role[AWS][SECURITY_GROUP] + ".id"
        setDefaultInMap(role[AWS], ROOT_VOLUME_TYPE, "gp2")

def groomConfig(model):
    model[DATA][KEY_PAIR_BY_ID] = {}
    for kp in model[CONFIG][AWS_KEY_PAIRS]:
        model[DATA][KEY_PAIR_BY_ID][kp[KEY_PAIR_ID]]  = kp
    
def lookupKeyPair(model, keyPairId):    
    for kp in model[CONFIG][AWS_KEY_PAIRS]:
        if kp[KEY_PAIR_ID] == keyPairId:
            return kp
    ERROR("Unable to find a key_pair_id == '{}' in configuration".format(keyPairId))
                
def groom(_plugin, model):
    groomConfig(model)
    model[DATA][REFERENCE_SUBNET]= model[CLUSTER][NODES][0][AWS][SUBNET]
    setDefaultInMap(model[CLUSTER][AWS], KEY_PAIR, "default")
    model[DATA][DATA_KEY_PAIR] = lookupKeyPair(model, model[CLUSTER][AWS][KEY_PAIR])
    groomSecurityGroups(model)
    groomRoles(model)
    model["data"]["buildScript"] = appendPath(model["data"]["targetFolder"], "build.sh")
    return True # Always enabled



