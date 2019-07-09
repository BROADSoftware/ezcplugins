# Kubspray follow up 

All this files in `snippets/group_vars` are copied as is from `inventory/local/group_vars`, except:

- all.yml, renamed to all.yml.200.jj2
- k8s-cluster/k8s-cluster.yml renamed k8s-cluster/k8s-cluster.yml.200.jj2 and with some modification marked with EZCLUSTER

# Proxy issue

If proxy must be set, there is a problem as `http_proxy` set both docker's proxy and yum proxy.

A quick fix is to replace `http_proxy` per `yum_http_proxy` in the following files:

- roles/bootstrap-os/tasks/bootstrap-centos.yml
- roles/container-engine/docker/tasks/main.yml
- roles/container-engine/docker/templates/rh_docker.repo.j2

A forked version solving this issue and intended to be used with this plugin is located at:

https://github.com/SergeAlexandre/kubespray/tree/bs2.10.4

# Proposal for http_proxy segregation

## What would you like to be added:

I suggest to replace the http_proxy variable by a more specific one, depending of the use case:

docker_http_proxy, for the docker service configuration
yum_http_proxy, for yum acces configuration.
ansible_http_proxy, used in proxy_env for the usage of ansible playbook (Typically on get_url) at build time.
Then we can have some default value to preserve compatibility:

docker_http_proxy: {{http_proxy}}
yum_http_proxy: {{http_proxy}}
ansible_http_proxy: {{http_proxy}}
(Of course same for https_proxy and no_proxy)

If you agree on this, I would be happy to implement it, make some test on Centos and make a PR.

(Another approach would be to completely remove yum proxy support from kubespray, considering yum 
configuration is out of its scope and should be performed before, as part of the base OS setup).

Please let me know what you think.

## Why is this needed:

Because there is some cases where these values need to be different. For example, I need to setup 
the proxy in docker configuration (targeting a specific docker proxy-cache) while still using direct yum access
on internally built yum repo. And may be a squid for usual (get_url) proxying.

