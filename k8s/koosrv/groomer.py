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

import os
from misc import setDefaultInMap,appendPath,ERROR

CLUSTER = "cluster"
DATA="data"
K8S="k8s"
KOOSRV="koosrv"
DISABLED = "disabled"
SSL_CERT_SRC="ssl_cert_src"
SSL_KEY_SRC="ssl_key_src"
SOURCE_FILE_DIR="sourceFileDir"


def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER], K8S, {})
    setDefaultInMap(model[CLUSTER][K8S], KOOSRV, {})
    setDefaultInMap(model[CLUSTER][K8S][KOOSRV], DISABLED, False)
    if model[CLUSTER][K8S][KOOSRV][DISABLED]:
        return False
    else:
        model[CLUSTER][K8S][KOOSRV][SSL_CERT_SRC] = appendPath(model[DATA][SOURCE_FILE_DIR], model[CLUSTER][K8S][KOOSRV][SSL_CERT_SRC])
        if not os.path.isfile( model[CLUSTER][K8S][KOOSRV][SSL_CERT_SRC]):
            ERROR("Unable to find '{}'!".format( model[CLUSTER][K8S][KOOSRV][SSL_CERT_SRC]))
        model[CLUSTER][K8S][KOOSRV][SSL_KEY_SRC] = appendPath(model[DATA][SOURCE_FILE_DIR], model[CLUSTER][K8S][KOOSRV][SSL_KEY_SRC])
        if not os.path.isfile( model[CLUSTER][K8S][KOOSRV][SSL_KEY_SRC]):
            ERROR("Unable to find '{}'!".format( model[CLUSTER][K8S][KOOSRV][SSL_KEY_SRC]))
        return True
