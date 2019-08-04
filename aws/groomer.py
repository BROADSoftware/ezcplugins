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

from misc import ERROR

CLUSTER="cluster"
DATA="data"
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

# In data part
REFERENCE_SUBNET="referenceSubnet"
EXTERNAL_SECURITY_GROUPS="externalSecurityGroups"
SECURITY_GROUP_BY_NAME="securityGroupByName"
INGRESS="ingress"
EGRESS="egress"
SECURITY_GROUP="security_group"
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

def computeTfSecurityGroupRule(model, rule):
    tf = {}
    if SOURCE in rule:
        peer = rule[SOURCE]
    else:
        peer = rule[DESTINATION]
    if peer == "ANY":
        tf[CIDR_BLOCK] = "0.0.0.0/0"
    elif peer == "SELF":
        tf[SELF] = True
    elif peer == "VPC":
        tf[CIDR_BLOCK] = "${data.aws_vpc.my_vpc.cidr_block}"
    elif isCidr(peer):
        tf[CIDR_BLOCK] = peer
    else:
        # Should be a reference to another SG.
        if peer in model[DATA][SECURITY_GROUP_BY_NAME]:
            tf[SECURITY_GROUP] = "${aws_security_group." + peer + ".id}"
        else:
            model[DATA][EXTERNAL_SECURITY_GROUPS].add(peer)
            tf[SECURITY_GROUP] = "${data.aws_security_group." + peer + ".id}"
    return tf
        
        

def groomSecurityGroups(model):
    model[DATA][EXTERNAL_SECURITY_GROUPS] = Set()
    model[DATA][SECURITY_GROUP_BY_NAME] = {}
    # First, a loop to find all our defined SG
    if SECURITY_GROUPS in model[CLUSTER][AWS]:
        for sg in model[CLUSTER][AWS][SECURITY_GROUPS]:
            model[DATA][SECURITY_GROUP_BY_NAME][sg[NAME]] = sg
        # Now, loop again to find all external (Should be pre-existing)
        for sg in model[CLUSTER][AWS][SECURITY_GROUPS]:
            sg[INGRESS] = []
            for inbound in sg[INBOUND_RULES]:
                sg[INGRESS].append(computeTfSecurityGroupRule(model, inbound))
            sg[EGRESS] = []
            for outbound in sg[OUTBOUND_RULES]:
                sg[EGRESS].append(computeTfSecurityGroupRule(model, outbound))
                
            
        
    
    
    

def groom(_plugin, model):
    model[DATA][REFERENCE_SUBNET]= model[CLUSTER][NODES][0][AWS][SUBNET]
    groomSecurityGroups(model)
    return True