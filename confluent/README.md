# Confluent platform.

Roles are copied 'as is' from :

    https://github.com/confluentinc/cp-ansible

tested with the following commit:

```
commit 8674d479fc8337fda91351c112d60b5d8ffa8054 (HEAD -> 5.0.x, origin/HEAD, origin/5.1.x, origin/5.0.x)
Author: Dustin Cote <dustin@confluent.io>
Date:   Fri Oct 26 08:37:40 2018 -0400

    Update README.md

commit e9e5b790ccdb3861e3b5b78e055c1672325e8396
Merge: f36121b 8a85185
Author: Dustin Cote <dustin@confluent.io>
Date:   Wed Oct 24 15:06:35 2018 -0400

    Merge pull request #68 from confluentinc/agoujet-ksql-listeners-fix

    Update main.yml

commit 8a851857557cc17a77d3f5ef227d2ef8087a20ce
Author: Aurelien <agoujet@parigo.net>
Date:   Mon Oct 22 18:09:45 2018 +0200

    Update main.yml

    issue with KSQL server with a host outside of a VPC. localhost doesn't work and 0.0.0.0 fix this issue.

```

Modifications are pushed to :

    https://github.com/mlahouar/cp-ansible
    branch : 5.2.X
    commit : 
        commit 6b762eff130ad262a7a62ab39a665ad01762c80b
        Author: moncef lahouar <moncef.lahouar@gmail.com>
        Date:   Tue Oct 22 10:50:18 2019 +0200
        
            Add SASL_SSL conf files
        



            
## HowTo

### Enable security
1. Define your security context on config file, ex : 

    ```
    ...
    security_contexts:
      confluent:
        - name: 'ml'
          mit_kdc:
            realm: 'ML.COM'
            server: mydomain.ml.com
            admin:
              login: 'admin/admin'
              password: 'AdminPassword'
          ssl:
            key_password: 'confluent1'
            keystore_password: 'confluent2'
            truststore_password: 'confluent3'
            ca_key_file: ../common/ca/CARoot.key
            ca_key_pass: 'confluent'
            ca_crt_file: ../common/ca/CARoot.crt
        - name: 'cib'
          active_directory:
            realm: 'ML.COM'
            uri: 'ldaps://dc1.dc2:636'
            container_dn: 'OU=....,DC=DC1,DC=DC2'
            rw_user:
              login: 'admin'
              password: 'AdminPassword'
    ...
    ```
2. Reference your security context on your cluster definition file:

    ```
    ...
    confluent:
      disabled: false
      repo_id: "RepoID"
      helper_id: "X.Y.Z"
      security:
        context: 'ml'           # sasl will be enable automatically if running inside a security context, remove security.context to have a non secured cluster
    ...
    ```


    
        

