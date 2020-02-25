
# Dashboard

login: admin

Password:

    kubectl -n rook-ceph-dir get secret rook-ceph-dashboard-password -o yaml | grep "password:" | awk '{print $2}' | base64 --decode

## Pb dashboard

    https://github.com/rook/rook/issues/3106
    
    #export OPTS="--cluster=rook-ceph-dev --conf=/var/lib/rook/rook-ceph-dev/rook-ceph-dev.config --keyring=/var/lib/rook/rook-ceph-dev/client.admin.keyring"
    #export OPTS="--cluster=rook-ceph-dir --conf=/var/lib/rook/rook-ceph-dir/rook-ceph-dir.config --keyring=/var/lib/rook/rook-ceph-dir/client.admin.keyring"
    
    ceph $OPTS dashboard ac-role-create admin-no-iscsi

    for scope in dashboard-settings log rgw prometheus grafana nfs-ganesha manager hosts rbd-image config-opt rbd-mirroring cephfs user osd pool monitor; do
        ceph $OPTS dashboard ac-role-add-scope-perms admin-no-iscsi ${scope} create delete read update;
    done

    ceph $OPTS dashboard ac-user-set-roles admin admin-no-iscsi
    	    
