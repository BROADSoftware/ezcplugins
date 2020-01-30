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

from misc import setDefaultInMap,appendPath,ERROR
import os

CLUSTER = "cluster"
DRPROXY="drproxy"
DISABLED = "disabled"
CERT_FILE = "cert_file"
KEY_FILE = "key_file"
ROOT_CA_FILE = "root_ca_file"
DATA="data"
SOURCE_FILE_DIR="sourceFileDir"

def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER][DRPROXY], DISABLED, False)
    if model[CLUSTER][DRPROXY][DISABLED]:
        return False
    else:
        for f in [CERT_FILE, KEY_FILE, ROOT_CA_FILE]:
            model[CLUSTER][DRPROXY][f] = appendPath(model[DATA][SOURCE_FILE_DIR], model[CLUSTER][DRPROXY][f])
            if not os.path.isfile(model[CLUSTER][DRPROXY][f]):
                ERROR("Unable to find '{}'!".format(model[CLUSTER][DRPROXY][f]))
        return True
