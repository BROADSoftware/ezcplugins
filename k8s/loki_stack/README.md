# LOKI ezcluster plugin

## WARNING: 

This is not PROD READY plugin:

- Grafana Authentication is not encrypted

- loki server access is fully open.

- Storage is only file based. Not scalable not reliable.

# logcli (On Mac OS)

```
cd /usr/local/bin
sudo cp /Users/myself/Downloads/logcli-darwin-amd64 ./logcli
sudo chmod +x ./logcli
logcli
```

Will fail due to Mac OS protection.
Launch with Finder and open ‘Preference systeme/Securité et confidentialité’ to allow it.

Then:

```
export LOKI_ADDR=http://loki.kspray1:3100
logcli labels namespace
```

Some sample:

```
logcli query '{namespace="kube-system"}'
logcli query -t --no-labels '{namespace="kube-system"}'
logcli query -t  --include-label=container_name  '{namespace="kube-system"}'
```

# Port forwarding

If for any reason, this is no metallb in front of grafana and/or loki, one may use kubectl port forwarding:

```
kubectl -n loki port-forward svc/loki-grafana 8080:80
```

Then, launch a browser to http://localhost:8080

And, for logcli:

```
kubectl -n loki port-forward svc/loki 3100:3100

# On another terminal
export LOKI_ADDR=http://localhost:3100

logcli labels namespace
```


