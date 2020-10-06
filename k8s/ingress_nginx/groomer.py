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

from misc import setDefaultInMap, ERROR, resolveDnsAndCheck

CLUSTER = "cluster"
K8S="k8s"
INGRESS_NGINX="ingress_nginx"
DISABLED = "disabled"
EXTERNAL_IP="external_ip"
ENABLE_SSL_PASSTHROUGH="enable_ssl_passthrough"
DASHBOARD_HOST="dashboard_host"
COMMAND_LINE_ARGUMENTS="command_line_arguments"

def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER], K8S, {})
    setDefaultInMap(model[CLUSTER][K8S], INGRESS_NGINX, {})
    setDefaultInMap(model[CLUSTER][K8S][INGRESS_NGINX], DISABLED, False)
    setDefaultInMap(model[CLUSTER][K8S][INGRESS_NGINX], ENABLE_SSL_PASSTHROUGH, False)
    if model[CLUSTER][K8S][INGRESS_NGINX][DISABLED]:
        return False
    else:
        model[CLUSTER][K8S][INGRESS_NGINX][EXTERNAL_IP] = resolveDnsAndCheck(model[CLUSTER][K8S][INGRESS_NGINX][EXTERNAL_IP])
        if DASHBOARD_HOST in model[CLUSTER][K8S][INGRESS_NGINX]:
            dashboard_ip = resolveDnsAndCheck(model[CLUSTER][K8S][INGRESS_NGINX][DASHBOARD_HOST])
            if model[CLUSTER][K8S][INGRESS_NGINX][EXTERNAL_IP] != dashboard_ip:
                ERROR("'external_ip' and 'dashboard_host' must resolve on same ip ({} != {})".format(model[CLUSTER][K8S][INGRESS_NGINX][EXTERNAL_IP], dashboard_ip))
            enableSslPassthrough = False
            if COMMAND_LINE_ARGUMENTS in model[CLUSTER][K8S][INGRESS_NGINX]:
                for cla in model[CLUSTER][K8S][INGRESS_NGINX][COMMAND_LINE_ARGUMENTS]:
                    if cla == "--enable-ssl-passthrough":
                        enableSslPassthrough = True 
            if not enableSslPassthrough:
                ERROR("Dashbaord access require '--enable-ssl-passthrough' command line argument to be defined")
        return True


