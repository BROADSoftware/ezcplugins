
# Dashboard

login: admin

Password:

    kubectl -n rook-ceph get secret rook-ceph-dashboard-password -o yaml | grep "password:" | awk '{print $2}' | base64 --decode

## Pb dashboard

    https://github.com/rook/rook/issues/3106
    
    ceph dashboard ac-role-create admin-no-iscsi

    for scope in dashboard-settings log rgw prometheus grafana nfs-ganesha manager hosts rbd-image config-opt rbd-mirroring cephfs user osd pool monitor; do
        ceph dashboard ac-role-add-scope-perms admin-no-iscsi ${scope} create delete read update;
    done

    ceph dashboard ac-user-set-roles admin admin-no-iscsi
    
A sample to grab option

    ceph osd crush rule create-simple replicapool3 default host --connect-timeout=15 --cluster=rook-ceph --conf=/var/lib/rook/rook-ceph/rook-ceph.config \
	    --keyring=/var/lib/rook/rook-ceph/client.admin.keyring --format json --out-file /tmp/348642040    
	    

## Pb locked namespace (Unresolved)

rook-ceph namespace can't be deleted/

View what is inside:

    kubectl api-resources --verbs=list --namespaced -o name   | xargs -n 1 kubectl get --show-kind --ignore-not-found -n rook-ceph

    NAME                                                     DATADIRHOSTPATH               MONCOUNT   AGE   STATE     HEALTH
    cephcluster.ceph.rook.io/kspray3.bsa.broadsoftware.com   /var/lib/rookceph/rook-ceph   3          16h   Created   HEALTH_OK
    cephcluster.ceph.rook.io/rook-ceph                       /var/lib/rookceph/rook-ceph   3          13h   Created   HEALTH_OK
	    
Tried:

    kubectl -n rook-ceph delete --grace-period=0 --force=true  cephcluster.ceph.rook.io/rook-ceph	    
	    	    
    kubectl -n rook-ceph delete --grace-period=0 --force=true  cephcluster.ceph.rook.io/kspray3.bsa.broadsoftware.com

Does not help.

To try:

    https://github.com/kubernetes/kubernetes/issues/60807
    
See also at the end of

    https://github.com/rook/rook/blob/master/Documentation/ceph-teardown.md	    
    
THIS LAST WORKS    