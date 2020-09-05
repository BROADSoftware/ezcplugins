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

from misc import setDefaultInMap, appendPath,lookupHelper,ERROR,lookupRepository,lookupHttpProxy
import os

K8S="k8s"
KUBESPRAY="kubespray"
HELPERS="helpers"
FOLDER="folder"
DATA="data"
ROLE_PATHS="rolePaths"
CONFIG_FILE = "configFile"
CLUSTER = "cluster"
DOCKER_CERTIFICATES = "docker_certificates"
DISABLED = "disabled"
CLUSTER_NAME="cluster_name"
K9S_REPO_ID="k9s_repo_id"
HELM_REPO_ID="helm_repo_id"
FILES_REPO_ID="files_repo_id"
METRICS_SERVER="metrics_server"
AUDIT="audit"
POD_SECURITY_POLICIES="pod_security_policies"

def groom(_plugin, model):
    setDefaultInMap(model[CLUSTER], K8S, {})
    setDefaultInMap(model[CLUSTER][K8S], KUBESPRAY, {})
    setDefaultInMap(model[CLUSTER][K8S][KUBESPRAY], DISABLED, False)
    setDefaultInMap(model[CLUSTER][K8S][KUBESPRAY], "basic_auth", False)
    setDefaultInMap(model[CLUSTER][K8S][KUBESPRAY], METRICS_SERVER, True)
    setDefaultInMap(model[CLUSTER][K8S][KUBESPRAY], AUDIT, False)
    setDefaultInMap(model[CLUSTER][K8S][KUBESPRAY], POD_SECURITY_POLICIES, True)
    if model[CLUSTER][K8S][KUBESPRAY][DISABLED]:
        return False
    else:
        lookupRepository(model, None, "docker_yum", model[CLUSTER][K8S][KUBESPRAY]['docker_yum_repo_id'])
        if K9S_REPO_ID in model[CLUSTER][K8S][KUBESPRAY]:
            lookupRepository(model, "k9s", repoId = model[CLUSTER][K8S][KUBESPRAY][K9S_REPO_ID])
        if HELM_REPO_ID in model[CLUSTER][K8S][KUBESPRAY]:
            lookupRepository(model, "helm", repoId = model[CLUSTER][K8S][KUBESPRAY][HELM_REPO_ID])
        lookupHelper(model, KUBESPRAY, helperId=model[CLUSTER][K8S][KUBESPRAY]["helper_id"])
        lookupHttpProxy(model, model[CLUSTER][K8S][KUBESPRAY]["docker_proxy_id"] if "docker_proxy_id" in model[CLUSTER][K8S][KUBESPRAY] else None, "docker")
        lookupHttpProxy(model, model[CLUSTER][K8S][KUBESPRAY]["master_root_proxy_id"] if "master_root_proxy_id" in model[CLUSTER][K8S][KUBESPRAY] else None, "master_root")
        lookupHttpProxy(model, model[CLUSTER][K8S][KUBESPRAY]["yumproxy_id"] if "yum_proxy_id" in model[CLUSTER][K8S][KUBESPRAY] else None, "yum")
        if FILES_REPO_ID in model[CLUSTER][K8S][KUBESPRAY]:
            lookupRepository(model, "kubespray_files", repoId=model[CLUSTER][K8S][KUBESPRAY][FILES_REPO_ID])
        model[DATA][ROLE_PATHS].add(appendPath(model[DATA][HELPERS][KUBESPRAY][FOLDER], "roles"))
        model[DATA]["dnsNbrDots"] = model[CLUSTER][K8S][KUBESPRAY][CLUSTER_NAME].count(".") + 1
        certByName = {}
        if DOCKER_CERTIFICATES in model["config"]:
            for cert in model["config"][DOCKER_CERTIFICATES]:
                cert["path"] = appendPath(os.path.dirname(model[DATA][CONFIG_FILE]), cert["path"])
                if not os.path.isfile(cert["path"]) or not os.access(cert["path"], os.R_OK):
                    ERROR("Configuration error: docker_certificates.{}: Invalid path '{}'".format(cert["name"],  cert["path"]))
                certByName[cert["name"]] = cert
        model[DATA][DOCKER_CERTIFICATES] = []
        if DOCKER_CERTIFICATES in model[CLUSTER][K8S][KUBESPRAY]:
            for certName in model[CLUSTER][K8S][KUBESPRAY][DOCKER_CERTIFICATES]:
                if certName in certByName:
                    cert = certByName[certName]
                    if "port" in cert:
                        cert["endpoint"] = "{}:{}".format(cert["host"], cert['port'])
                    else:
                        cert["endoint"] = cert["host"]
                    model[DATA][DOCKER_CERTIFICATES].append(cert)
                else:
                    ERROR("docker_certificates '{}' is not defined in configuration file!".format(certName))
        return True

