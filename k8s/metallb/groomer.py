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

from misc import setDefaultInMap, ERROR
import ipaddress

CLUSTER = "cluster"
K8S="k8s"
METALLB="metallb"
DISABLED = "disabled"
EXTERNAL_IP_RANGES="external_ip_ranges"
FIRST="first"
LAST="last"
DASHBOARD_IP="dashboard_ip"

def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER], K8S, {})
    setDefaultInMap(model[CLUSTER][K8S], METALLB, {})
    setDefaultInMap(model[CLUSTER][K8S][METALLB], DISABLED, False)
    if model[CLUSTER][K8S][METALLB][DISABLED]:
        return False
    else:
        for rangeip in model[CLUSTER][K8S][METALLB][EXTERNAL_IP_RANGES]:
            first_ip = ipaddress.ip_address(u"" + rangeip[FIRST])
            last_ip = ipaddress.ip_address(u"" + rangeip[LAST])
            if not last_ip > first_ip:
                ERROR("Invalid metallb.external_ip_range (first >= last)")
        if DASHBOARD_IP in model[CLUSTER][K8S][METALLB]:
            db_ip =  ipaddress.ip_address(u"" + model[CLUSTER][K8S][METALLB][DASHBOARD_IP])
            if db_ip < first_ip or db_ip > last_ip:
                ERROR("metallb.dashboard_ip is not included in metallb.external_ip_range")
        return True
