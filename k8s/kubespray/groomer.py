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

from misc import setDefaultInMap, appendPath,lookupHelper,ERROR
import os

KUBESPRAY="kubespray"
HELPERS="helpers"
FOLDER="folder"
DATA="data"
ROLE_PATHS="rolePaths"
CONFIG_FILE = "configFile"

def groom(_plugin, model):
    setDefaultInMap(model["cluster"], "kubespray", {})
    setDefaultInMap(model["cluster"]["kubespray"], "disabled", False)
    setDefaultInMap(model["cluster"]["kubespray"], "basic_auth", False)
    if model["cluster"]["kubespray"]["disabled"]:
        return False
    else:
        lookupHelper(model, KUBESPRAY)
        model[DATA][ROLE_PATHS].add(appendPath(model[DATA][HELPERS][KUBESPRAY][FOLDER], "roles"))
        model["data"]["dnsNbrDots"] = model["cluster"]["domain"].count(".") + 1
        certByName = {}
        if "docker_certificates" in model["config"]:
            for cert in model["config"]["docker_certificates"]:
                cert["path"] = appendPath(os.path.dirname(model[DATA][CONFIG_FILE]), cert["path"])
                if not os.path.isfile(cert["path"]) or not os.access(cert["path"], os.R_OK):
                    ERROR("Configuration error: docker_certificates.{}: Invalid path '{}'".format(cert["name"],  cert["path"]))
                certByName[cert["name"]] = cert
        model["data"]["docker_certificates"] = []
        if "docker_certificates" in model["cluster"]["kubespray"]:
            for certName in model["cluster"]["kubespray"]["docker_certificates"]:
                if certName in certByName:
                    cert = certByName[certName]
                    if "port" in cert:
                        cert["endpoint"] = "{}:{}".format(cert["host"], cert['port'])
                    else:
                        cert["endoint"] = cert["host"]
                    model["data"]["docker_certificates"].append(cert)
                else:
                    ERROR("docker_certificates '{}' is not defined in configuration file!".format(certName))
        return True

