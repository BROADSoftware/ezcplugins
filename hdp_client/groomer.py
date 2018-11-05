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

HD_CLIENT = "hdp_client"
CLUSTER = "cluster"
DISABLED = "disabled"
HORTONWORKS = "hortonworks"
AMBARI_SERVER_URL = "ambari_server_url"

def groom(plugin, model):
    setDefaultInMap(model[CLUSTER][HD_CLIENT], DISABLED, False)
    if model[CLUSTER][HD_CLIENT][DISABLED]:
        return False
    else:
        lookupRepository(model, HD_CLIENT, HORTONWORKS)
        if model[CLUSTER][HD_CLIENT][AMBARI_SERVER_URL].endswith("/"):
            model[CLUSTER][HD_CLIENT][AMBARI_SERVER_URL] = model[CLUSTER][HD_CLIENT][AMBARI_SERVER_URL][:-1]
        return True
