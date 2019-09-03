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

from urlparse import urlparse
from misc import setDefaultInMap,lookupHttpProxy

CLUSTER = "cluster"
DOCKER_NEXUS_PROXY = "docker_nexus_proxy"
DOCKER_NEXUS_NEXT_PROXY = "docker_nexus_next_proxy"
DISABLED = "disabled"
NEXT_PROXY_ID = "next_proxy_id"
DATA="data"
HTTPPROXIES="httpProxies"
HTTP_PROXY="http_proxy"
HTTPS_PROXY="https_proxy"
NEXT_PROXY_HTTP="next_proxy_http"
NEXT_PROXY_HTTPS="next_proxy_https"
HOST="host"
PORT="port"
USERNAME="username"
PASSWORD="password"
NO_PROXY="no_proxy"
NO_PROXY_JAVA="no_proxy_java"

def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER][DOCKER_NEXUS_PROXY], DISABLED, False)
    if model[CLUSTER][DOCKER_NEXUS_PROXY][DISABLED]:
        return False
    else:
        setDefaultInMap(model[CLUSTER][DOCKER_NEXUS_PROXY], "nexus_default_port", 8081)
        setDefaultInMap(model[CLUSTER][DOCKER_NEXUS_PROXY], "nexus_internal_docker_port", 8082)
        setDefaultInMap(model[DATA], DOCKER_NEXUS_PROXY, {})
        if NEXT_PROXY_ID in model[CLUSTER][DOCKER_NEXUS_PROXY]:
            lookupHttpProxy(model, model[CLUSTER][DOCKER_NEXUS_PROXY][NEXT_PROXY_ID], DOCKER_NEXUS_NEXT_PROXY)
            proxy = model[DATA][HTTPPROXIES][DOCKER_NEXUS_NEXT_PROXY]
            if HTTP_PROXY in proxy:
                x = urlparse(proxy[HTTP_PROXY])
                model[DATA][DOCKER_NEXUS_PROXY][NEXT_PROXY_HTTP] = {}
                model[DATA][DOCKER_NEXUS_PROXY][NEXT_PROXY_HTTP][HOST] = x.hostname
                model[DATA][DOCKER_NEXUS_PROXY][NEXT_PROXY_HTTP][PORT] = x.port
                model[DATA][DOCKER_NEXUS_PROXY][NEXT_PROXY_HTTP][USERNAME] = x.username if x.username is not None else ""
                model[DATA][DOCKER_NEXUS_PROXY][NEXT_PROXY_HTTP][PASSWORD] = x.password if x.password is not None else ""
            if HTTPS_PROXY in proxy:
                x = urlparse(proxy[HTTPS_PROXY])
                model[DATA][DOCKER_NEXUS_PROXY][NEXT_PROXY_HTTPS] = {}
                model[DATA][DOCKER_NEXUS_PROXY][NEXT_PROXY_HTTPS][HOST] = x.hostname
                model[DATA][DOCKER_NEXUS_PROXY][NEXT_PROXY_HTTPS][PORT] = x.port
                model[DATA][DOCKER_NEXUS_PROXY][NEXT_PROXY_HTTPS][USERNAME] = x.username if x.username is not None else ""
                model[DATA][DOCKER_NEXUS_PROXY][NEXT_PROXY_HTTPS][PASSWORD] = x.password if x.password is not None else ""
            if NO_PROXY_JAVA in proxy:
                model[DATA][DOCKER_NEXUS_PROXY][NO_PROXY] = proxy[NO_PROXY_JAVA].split(",")
                
                
        return True
    
