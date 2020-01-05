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

from misc import setDefaultInMap,lookupRepository,appendPath,ERROR
import os

CLUSTER = "cluster"
HARBOR="harbor"
DISABLED = "disabled"
REPO_ID="repo_id"
SSL_CERT_SRC="ssl_cert_src"
SSL_KEY_SRC="ssl_key_src"
DATA="data"
SOURCE_FILE_DIR="sourceFileDir"
VALIDATE_API_CERT="validate_api_cert"
HOSTNAME="hostname"


def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER], HARBOR, {})
    setDefaultInMap(model[CLUSTER][HARBOR], DISABLED, False)
    if model[CLUSTER][HARBOR][DISABLED]:
        return False
    else:
        lookupRepository(model, "harbor", repoId = model[CLUSTER][HARBOR][REPO_ID])
        model[CLUSTER][HARBOR][SSL_CERT_SRC] = appendPath(model[DATA][SOURCE_FILE_DIR], model[CLUSTER][HARBOR][SSL_CERT_SRC])
        if not os.path.isfile( model[CLUSTER][HARBOR][SSL_CERT_SRC]):
            ERROR("Unable to find '{}'!".format( model[CLUSTER][HARBOR][SSL_CERT_SRC]))
        model[CLUSTER][HARBOR][SSL_KEY_SRC] = appendPath(model[DATA][SOURCE_FILE_DIR], model[CLUSTER][HARBOR][SSL_KEY_SRC])
        if not os.path.isfile( model[CLUSTER][HARBOR][SSL_KEY_SRC]):
            ERROR("Unable to find '{}'!".format( model[CLUSTER][HARBOR][SSL_KEY_SRC]))
        setDefaultInMap(model[CLUSTER][HARBOR], VALIDATE_API_CERT, False)
        setDefaultInMap(model[CLUSTER][HARBOR], HOSTNAME, "{{ ansible_fqdn }}")
        return True
