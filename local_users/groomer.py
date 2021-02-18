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

from misc import ERROR

CONFIG="config"
DATA="data"
CLUSTER="cluster"
LOCAL_USERS="local_users"
LOGIN="login"


def list_to_map(list, key):
    m = {}
    for x in list:
        m[x[key]] = x
    return m


def groom(_plugin, model):
    if LOCAL_USERS in model[CLUSTER] and len(model[CLUSTER][LOCAL_USERS]) > 0:
        if LOCAL_USERS not in model[CONFIG]:
            ERROR("Missing 'local_users' entries in configuration")
        userMap = list_to_map(model[CONFIG][LOCAL_USERS], LOGIN)
        model[DATA][LOCAL_USERS] = []
        for login in model[CLUSTER][LOCAL_USERS]:
            if login in userMap:
                model[DATA][LOCAL_USERS].append(userMap[login])
            else:
                ERROR("Missing definition of user '{}' in configuration.".format(login))
    return True
