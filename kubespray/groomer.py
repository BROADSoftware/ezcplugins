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

from misc import setDefaultInMap, appendPath,lookupHelper


KUBESPRAY="kubespray"
HELPERS="helpers"
FOLDER="folder"
DATA="data"
ROLE_PATHS="rolePaths"

def groom(plugin, model):
    setDefaultInMap(model["cluster"], "kubespray", {})
    setDefaultInMap(model["cluster"]["kubespray"], "disabled", False)
    if model["cluster"]["kubespray"]["disabled"]:
        return False
    else:
        lookupHelper(model, KUBESPRAY)
        model[DATA][ROLE_PATHS].add(appendPath(model[DATA][HELPERS][KUBESPRAY][FOLDER], "roles"))
        model["data"]["dnsNbrDots"] = model["cluster"]["domain"].count(".") + 1
        return True

