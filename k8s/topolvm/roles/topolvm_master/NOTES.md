
## manifest.yaml.j2 build

git clone topolvm and check out appropriate version

In deploy/manifests/base, edit kustomization.yaml
- Comment out provisionner.yaml (The storage-class will be defined elsewhere)
- Add certificates.yaml in the ressources list
- Add at the end: 
    patchesStrategicMerge:
   - patch.yaml
      
```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - crd.yaml
  - controller.yaml
  - mutatingwebhooks.yaml
  - namespace.yaml
  - node.yaml
#  - provisioner.yaml
  - psp.yaml
  - scheduler.yaml
  - certificates.yaml
configMapGenerator:
  - name: scheduler-options
    namespace: topolvm-system
    files:
      - scheduler-options.yaml
patchesStrategicMerge:
  - patch.yaml 
```

And add patch.yaml with the following
    
```
apiVersion: apps/v1
kind: DaemonSet
metadata:
  namespace: topolvm-system
  name: node
spec:
  template:
    spec:
      nodeSelector:
        topology.topolvm.cybozu.com: "true"
```

Then in the root folder of topolvm:

```
mkdir /tmp
kustomize build ./deploy/manifests/overlays/daemonset-scheduler >./tmp/manifest.yaml.j2
```

## Other files

- scheduler-config and scheduler-policy are copies as is, from deploy/scheduler-config
- storage_classes should be adjusted 

