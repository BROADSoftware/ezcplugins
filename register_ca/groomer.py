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


from misc import setDefaultInMap,resolveDns,appendPath,ERROR
import os

CLUSTER = "cluster"
REGISTER_CA = "register_ca"
DISABLED = "disabled"
DATA="data"
SOURCE_FILE_DIR="sourceFileDir"
SRC="src"
NAME="name"
PATHS="paths"
URLS="urls"
FROM_PATHS="from_paths"


def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER][REGISTER_CA], DISABLED, False)
    if model[CLUSTER][REGISTER_CA][DISABLED]:
        return False
    else:
        if FROM_PATHS in model[CLUSTER][REGISTER_CA]:
            for idx, p in  enumerate(model[CLUSTER][REGISTER_CA][FROM_PATHS]):
                model[CLUSTER][REGISTER_CA][FROM_PATHS][idx][SRC] = appendPath(model[DATA][SOURCE_FILE_DIR], p[SRC])
                if not os.path.isfile(model[CLUSTER][REGISTER_CA][FROM_PATHS][idx][SRC]):
                    ERROR("Unable to find '{}'!".format( model[CLUSTER][REGISTER_CA][FROM_PATHS][idx][SRC]))
        return True
    



