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

from misc import ERROR,lookupRepository,setDefaultInMap

POSTGRESQL_SERVER = "postgresql_server"
CLUSTER = "cluster"
DISABLED = "disabled"
PASSWORD = "password"
ENCRYPTED_PASSWORD = "encrypted_password"

def groom(plugin, model):
    setDefaultInMap(model[CLUSTER][POSTGRESQL_SERVER], DISABLED, False)
    if model[CLUSTER][POSTGRESQL_SERVER][DISABLED]:
        return False
    else:
        lookupRepository(model, POSTGRESQL_SERVER)
        if PASSWORD in model[CLUSTER][POSTGRESQL_SERVER]:
            if ENCRYPTED_PASSWORD in model[CLUSTER][POSTGRESQL_SERVER]:
                ERROR("posgresql_server: 'password' and 'encrypted_password' can't be both defined!")
            else:
                print("\n**WARNING**: usage of clear text password is discouraged. Use 'encrypted_password' instead.")
                print("To encrypt a password: python -c \"import hashlib; print hashlib.md5('yourPassword'+'yourUser').hexdigest()\"\n")
        return True
