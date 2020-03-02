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

from misc import setDefaultInMap,lookupRepository,ERROR, resolveDnsAndCheck
import ipaddress
 
 
CLUSTER = "cluster"
K8S="k8s"
DATA="data"
LOKI_STACK="loki_stack"
DISABLED = "disabled"
REPO_ID="repo_id"
STORAGE_CLASS="storage_class"
PERSISTENCE="persistence"
SIZE_GB="size_gb"
GRAFANA="grafana"
PROMETHEUS="prometheus"
LB_ADDRESS="lb_address"
METALLB="metallb"
EXTERNAL_IP_RANGES="external_ip_ranges"
FIRST="first"
LAST="last"
NAMESPACE="namespace"
LOKI="loki"
SERVER="server"
ALERT_MANAGER="alert_manager"

def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER][K8S][LOKI_STACK], DISABLED, False)
    setDefaultInMap(model[DATA], K8S, {})
    setDefaultInMap(model[DATA][K8S],LOKI_STACK, {})
    if model[CLUSTER][K8S][LOKI_STACK][DISABLED]:
        return False
    else:
        setDefaultInMap(model[CLUSTER][K8S][LOKI_STACK], NAMESPACE, "loki")
        # -------------- Loki parameters checking
        lookupRepository(model, None, "loki", model[CLUSTER][K8S][LOKI_STACK][REPO_ID])
        setDefaultInMap(model[CLUSTER][K8S][LOKI_STACK][LOKI], DISABLED, False)
        if not model[CLUSTER][K8S][LOKI_STACK][LOKI][DISABLED]:
            if PERSISTENCE not in model[CLUSTER][K8S][LOKI_STACK][LOKI]:
                ERROR("A 'loki.persistence map' must be defined if 'loki' is not disabled.")
            setDefaultInMap(model[CLUSTER][K8S][LOKI_STACK][LOKI][PERSISTENCE], DISABLED, False)
            if not model[CLUSTER][K8S][LOKI_STACK][LOKI][PERSISTENCE][DISABLED]:
                if STORAGE_CLASS not in model[CLUSTER][K8S][LOKI_STACK][LOKI][PERSISTENCE]:
                    ERROR("A 'storage_class' must be defined if 'persistence' is enabled on 'loki'")
                if SIZE_GB not in model[CLUSTER][K8S][LOKI_STACK][LOKI][PERSISTENCE]:
                    ERROR("A 'size_gb' must be defined if 'persistence' is enabled on 'loki'")
        # -------------- grafana parameters checking
        setDefaultInMap(model[CLUSTER][K8S][LOKI_STACK][GRAFANA], DISABLED, False)
        if not model[CLUSTER][K8S][LOKI_STACK][GRAFANA][DISABLED]:
            if PERSISTENCE not in model[CLUSTER][K8S][LOKI_STACK][GRAFANA]:
                ERROR("A 'grafana.persistence' map must be defined if 'grafana' is not disabled.")
            setDefaultInMap(model[CLUSTER][K8S][LOKI_STACK][GRAFANA][PERSISTENCE], DISABLED, False)
            if not model[CLUSTER][K8S][LOKI_STACK][GRAFANA][PERSISTENCE][DISABLED]:
                if STORAGE_CLASS not in model[CLUSTER][K8S][LOKI_STACK][GRAFANA][PERSISTENCE]:
                    ERROR("A 'storage_class' must be defined if 'persistence' is enabled on 'loki.grafana'")
                if SIZE_GB not in model[CLUSTER][K8S][LOKI_STACK][GRAFANA][PERSISTENCE]:
                    ERROR("A 'size_gb' must be defined if 'grafana.persistence' is enabled on 'loki.grafana'")
        # -------------- prometheus parameters checking
        setDefaultInMap(model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS], DISABLED, False)
        if not model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][DISABLED]:
            if SERVER not in model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS]:
                ERROR("A 'server' map must be defined if 'loki.prometheus' is defined")
            setDefaultInMap(model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][SERVER], DISABLED, False)
            if not model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][SERVER][DISABLED]:
                if PERSISTENCE not in model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][SERVER]:
                    ERROR("A 'loki.prometheus.server.persistence' map must be defined if 'loki.prometheus.server' is not disabled.")
                setDefaultInMap(model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][SERVER][PERSISTENCE], DISABLED, False)
                if not model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][SERVER][PERSISTENCE][DISABLED]:
                    if STORAGE_CLASS not in model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][SERVER][PERSISTENCE]:
                        ERROR("A 'storage_class' must be defined if 'persistence' is enabled on 'loki.prometheus.server'")
                    if SIZE_GB not in model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][SERVER][PERSISTENCE]:
                        ERROR("A 'size_gb' must be defined if 'persistence' is enabled on 'loki.prometheus.server'")
            if ALERT_MANAGER not in model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS]:
                ERROR("An 'alert_manager' map must be defined if 'loki.prometheus' is defined")
            setDefaultInMap(model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][ALERT_MANAGER], DISABLED, False)
            if not model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][ALERT_MANAGER][DISABLED]:
                if PERSISTENCE not in model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][ALERT_MANAGER]:
                    ERROR("A 'loki.prometheus.alert_manager.persistence' map must be defined if 'loki.prometheus.alert_manager' is not disabled.")
                setDefaultInMap(model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][ALERT_MANAGER][PERSISTENCE], DISABLED, False)
                if not model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][ALERT_MANAGER][PERSISTENCE][DISABLED]:
                    if STORAGE_CLASS not in model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][ALERT_MANAGER][PERSISTENCE]:
                        ERROR("A 'storage_class' must be defined if 'persistence' is enabled on 'loki.prometheus.alert_manager'")
                    if SIZE_GB not in model[CLUSTER][K8S][LOKI_STACK][PROMETHEUS][ALERT_MANAGER][PERSISTENCE]:
                        ERROR("A 'size_gb' must be defined if 'persistence' is enabled on 'loki.prometheus.alert_manager'")
        return True

def groom2(_plugin, model):
    if LB_ADDRESS in model[CLUSTER][K8S][LOKI_STACK][GRAFANA]:
        if METALLB not in model[CLUSTER][K8S] or model[CLUSTER][K8S][METALLB][DISABLED]:
            ERROR("A lb_address is defined while there is no metallb plugin")
        model[CLUSTER][K8S][LOKI_STACK][GRAFANA][LB_ADDRESS] = resolveDnsAndCheck(model[CLUSTER][K8S][LOKI_STACK][GRAFANA][LB_ADDRESS])
        lb_address =  ipaddress.ip_address(u"" + model[CLUSTER][K8S][LOKI_STACK][GRAFANA][LB_ADDRESS])

        lbAddressInRange = False
        for rangeip in model[CLUSTER][K8S][METALLB][EXTERNAL_IP_RANGES]:
            first_ip = ipaddress.ip_address(u"" + rangeip[FIRST])
            last_ip = ipaddress.ip_address(u"" + rangeip[LAST])
            if lb_address >= first_ip and lb_address <= last_ip:
                lbAddressInRange = True
        if not lbAddressInRange:
            ERROR("grafana.lb_address is not included in one of metallb.external_ip_ranges")

    if LB_ADDRESS in model[CLUSTER][K8S][LOKI_STACK][LOKI]:
        if METALLB not in model[CLUSTER][K8S] or model[CLUSTER][K8S][METALLB][DISABLED]:
            ERROR("A lb_address is defined while there is no metallb plugin")
        model[CLUSTER][K8S][LOKI_STACK][LOKI][LB_ADDRESS] = resolveDnsAndCheck(model[CLUSTER][K8S][LOKI_STACK][LOKI][LB_ADDRESS])
        lb_address =  ipaddress.ip_address(u"" + model[CLUSTER][K8S][LOKI_STACK][LOKI][LB_ADDRESS])

        lbAddressInRange = False
        for rangeip in model[CLUSTER][K8S][METALLB][EXTERNAL_IP_RANGES]:
            first_ip = ipaddress.ip_address(u"" + rangeip[FIRST])
            last_ip = ipaddress.ip_address(u"" + rangeip[LAST])
            if lb_address >= first_ip and lb_address <= last_ip:
                lbAddressInRange = True
        if not lbAddressInRange:
            ERROR("loki.lb_address is not included in one of metallb.external_ip_ranges")

        
    