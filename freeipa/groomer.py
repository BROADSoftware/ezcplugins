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
from misc import setDefaultInMap, appendPath,lookupHelper,ERROR

CLUSTER = "cluster"
FREEIPA="freeipa"
DISABLED = "disabled"
DATA="data"
HELPERS="helpers"
ROLE_PATHS="rolePaths"
FOLDER="folder"
CERT_FILES="cert_files"
SOURCE_FILE_DIR="sourceFileDir"

FILES_TO_COPY="filesToCopy"
SRC="src"
DEST="dest"
EXTERNAL_CERT_FILES="externalCertFiles"

USERS="users"
UPDATE_PASSWORD="update_password"
FIRSTNAME="firstname"
LASTNAME="lastname"
CN="cn"
DISPLAYNAME="displayname"
INITALS="initials"


def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER], FREEIPA, {})
    setDefaultInMap(model[CLUSTER][FREEIPA], DISABLED, False)
    if model[CLUSTER][FREEIPA][DISABLED]:
        return False
    else:
        model[DATA][FREEIPA] = {}
        lookupHelper(model, FREEIPA, helperId=model[CLUSTER][FREEIPA]["helper_id"])
        model[DATA][ROLE_PATHS].add(appendPath(model[DATA][HELPERS][FREEIPA][FOLDER], "roles"))
        if CERT_FILES in model[CLUSTER][FREEIPA] and len(model[CLUSTER][FREEIPA][CERT_FILES]) > 0:
            # NB: ipaserver_external_cert_files_from_controller does not works! (Missing basename in the copy). Will handle ourself before
            # In fact, was unable to transfer root authority from one install to another. A new CA is generated on each freeipa build.
            model[DATA][FREEIPA][FILES_TO_COPY] = []
            model[DATA][FREEIPA][EXTERNAL_CERT_FILES] = []
            for fn in model[CLUSTER][FREEIPA][CERT_FILES]:
                fc = {}
                fc[SRC] = appendPath(model[DATA][SOURCE_FILE_DIR], fn)
                if not os.path.isfile(fc[SRC]):
                    ERROR("Unable to find '{}'!".format(fc[SRC]))
                fc[DEST] = os.path.join("/root/", os.path.basename(fc[SRC]))
                model[DATA][FREEIPA][FILES_TO_COPY].append(fc)
                model[DATA][FREEIPA][EXTERNAL_CERT_FILES].append(fc[DEST])
        if USERS in model[CLUSTER][FREEIPA]:
            for user in model[CLUSTER][FREEIPA][USERS]:
                setDefaultInMap(user, UPDATE_PASSWORD, "on_create")
                # We better provide some default here than letting freeipa doing it. This for better control, and for updating (freeipi does not modify them once set).
                n = "{} {}".format(user[FIRSTNAME], user[LASTNAME])
                setDefaultInMap(user, CN, n)
                setDefaultInMap(user, DISPLAYNAME, n)
                setDefaultInMap(user, INITALS, (user[FIRSTNAME][0] + user[LASTNAME][0]).upper())
                
                
        return True

