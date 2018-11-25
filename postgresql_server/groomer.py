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

import hashlib
from misc import ERROR,lookupRepository,setDefaultInMap

POSTGRESQL_SERVER = "postgresql_server"
CLUSTER = "cluster"
DISABLED = "disabled"
PASSWORD = "password"
USERS = "users"
DATABASES = "databases"
NAME="name"

def groom(plugin, model):
    setDefaultInMap(model[CLUSTER][POSTGRESQL_SERVER], DISABLED, False)
    if model[CLUSTER][POSTGRESQL_SERVER][DISABLED]:
        return False
    else:
        setDefaultInMap(model[CLUSTER][POSTGRESQL_SERVER], USERS, [])
        setDefaultInMap(model[CLUSTER][POSTGRESQL_SERVER], DATABASES, [])       # To ease templates
        lookupRepository(model, POSTGRESQL_SERVER)
        unencryptedCount = 0
        if PASSWORD in model[CLUSTER][POSTGRESQL_SERVER]:
            if not model[CLUSTER][POSTGRESQL_SERVER][PASSWORD].startswith("md5"):
                unencryptedCount += 1
                # Will encrypt password, as unencrypted ones may be unsupported in future postgresl releases
                model[CLUSTER][POSTGRESQL_SERVER][PASSWORD] = "md5" + hashlib.md5(model[CLUSTER][POSTGRESQL_SERVER][PASSWORD] + 'postgres').hexdigest()
        for user in model[CLUSTER][POSTGRESQL_SERVER][USERS]:
            if not user[PASSWORD].startswith("md5"):
                unencryptedCount += 1
                user[PASSWORD] = "md5" + hashlib.md5(user[PASSWORD] + user[NAME]).hexdigest()
        if unencryptedCount > 0:
            print("")
            print("**WARNING**: usage of clear text password is discouraged.")
            print("To encrypt a password: \n\tpython -c \"import hashlib; print 'md5' + hashlib.md5('yourPassword'+'yourUser').hexdigest()\"")
            print("And set result in place of clear text password.")
        return True
