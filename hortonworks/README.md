# HDP plugin

To use with:
https://github.com/hortonworks/ansible-hortonworks

tested with the following commit:

```
commit 6f31278897f3ef8eccbb853e71ab94d8dc134e9e (HEAD -> master, origin/master, origin/HEAD)
Author: Alexandru Anghel <alexandru.anghel@gmail.com>
Date:   Thu Oct 18 21:32:02 2018 +0100

    Use the files lookup plugin for static blueprints.
```

## Patches of ansible-hortonworks

### playbooks/group_vars/all

As we use the playbook in this tree, we generate a conflict by using the group_vars/all located alongside.

Solution is to rename `playbooks/group_vars/all` to `playbooks/group_vars/all_xx`  in the ansible-hortonworks repo

### Blueprint

The file playbooks/roles/ambari-blueprint/templates/blueprint_dynamic.j2 need to be patched

In the `hdfs-site` section, the line

```
        "dfs.datanode.data.dir" : "/hadoop/hdfs/data",
```
        
Must be replaced by:

```
{% if dfs_datanode_dirs is defined %}
        "dfs.datanode.data.dir" : "{% for dir in dfs_datanode_dirs %}{% if not loop.first %},{%endif%}{{ dir }}/hadoop/hdfs/data{% endfor %}",
{% else %}
        "dfs.datanode.data.dir" : "/hadoop/hdfs/data",
{% endif %}
```

in the `kafka-broker` section, following must be added:

```
{% if kafka_log_dirs is defined %}
        ,"log.dirs" : "{% for dir in kafka_log_dirs %}{% if not loop.first %},{%endif%}{{ dir }}/kafka_logs{% endfor %}"
{% endif %}

```

## JDK - Embeded mode:

This mode does not set -j option of Ambari. Then:

By default when you do not specify this option, Setup automatically downloads the JDK binary to /var/lib/ambari-server/resources and installs the JDK to /usr/jdk64.

Ref:
https://ambari.apache.org/1.2.1/installing-hadoop-using-ambari/content/ambari-chap2-2-1.html


## Expected repository layout (HDP 2.6.5):

This layout is somewhat hard coded into the playbooks.
 
See https://github.com/hortonworks/ansible-hortonworks/blob/master/playbooks/roles/ambari-config/tasks/main.yml and https://github.com/hortonworks/ansible-hortonworks/blob/master/playbooks/roles/ambari-repo/tasks/main.yml

Unfortunatly, seems provided repo as tar file does not comply. So they will need to be adjusted


``` 
.
├── ambari
│   └── centos7
│       └── 2.x
│           └── updates
│               └── 2.6.2.2
│                   ├── ambari
│                   ├── repodata
│                   ├── RPM-GPG-KEY
│                   ├── smartsense
│                   └── tars
│                       ├── ambari
│                       └── smartsense
├── HDP
│   └── centos7
│       └── 2.x
│           └── updates
│               └── 2.6.5.0
│                   ├── accumulo
│                   ├── atlas
│                   ├── bigtop-jsvc
|                   .......
│                   ├── tez
│                   ├── tez_hive2
│                   ├── vrpms
│                   │   ├── accumulo
│                   │   ├── atlas
|                   ...............
│                   │   ├── zeppelin
│                   │   └── zookeeper
│                   ├── zeppelin
│                   └── zookeeper
├── HDP-GPL
│   └── centos7
│       └── 2.x
│           └── updates
│               └── 2.6.5.0
│                   ├── hadooplzo
│                   ├── repodata
│                   ├── RPM-GPG-KEY
│                   └── vrpms
│                       └── hadooplzo
└── HDP-UTILS-1.1.0.22
    └── repos
        └── centos7
            ├── openblas
            ├── repodata
            ├── RPM-GPG-KEY
            └── snappy

102 directories
```

here is a scripts to setup this 


Initial layout:

```
-rw-r--r--@ 1 sa  staff  7249933344 Oct 23 14:23 HDP-2.6.5.0-centos7-rpm.tar.gz
-rw-r--r--@ 1 sa  staff      328623 Oct 23 14:06 HDP-GPL-2.6.5.0-centos7-gpl.tar.gz
-rw-r--r--@ 1 sa  staff    90606616 Oct 23 14:06 HDP-UTILS-1.1.0.22-centos7.tar.gz
-rw-r--r--@ 1 sa  staff  1823779835 Oct 23 11:40 ambari-2.6.2.2-centos7.tar.gz
-rwxr-xr-x@ 1 sa  staff         600 Oct 24 22:36 setup.sh*
```

setup265.sh:

```
mkdir hdp2.6.5
cd hdp2.6.5

tar xvzf ../ambari-2.6.2.2-centos7.tar.gz
mkdir -p ambari/centos7/2.x/updates
mv ambari/centos7/2.6.2.2-1 ambari/centos7/2.x/updates/2.6.2.2

tar xvzf ../HDP-GPL-2.6.5.0-centos7-gpl.tar.gz
mkdir -p HDP-GPL/centos7/2.x/updates
mv HDP-GPL/centos7/2.6.5.0-292 HDP-GPL/centos7/2.x/updates/2.6.5.0

tar xvzf ../HDP-UTILS-1.1.0.22-centos7.tar.gz
mkdir -p HDP-UTILS-1.1.0.22/repos
mv HDP-UTILS/centos7/1.1.0.22 HDP-UTILS-1.1.0.22/repos/centos7

tar xvzf ../HDP-2.6.5.0-centos7-rpm.tar.gz
mkdir -p HDP/centos7/2.x/updates
mv HDP/centos7/2.6.5.0-292 HDP/centos7/2.x/updates/2.6.5.0
```


setup310.sh

```
mkdir hdp3.1.0
cd hdp3.1.0

SRC=/Users/xxxx/Downloads/hdp310

tar xvzf ${SRC}/ambari-2.7.3.0-centos7.tar.gz
mkdir -p ambari/centos7/2.x/updates
mv ambari/centos7/2.7.3.0-139 ambari/centos7/2.x/updates/2.7.3.0

tar xvzf ${SRC}/HDP-GPL-3.1.0.0-centos7-gpl.tar.gz
mkdir -p HDP-GPL/centos7/3.x/updates
mv HDP-GPL/centos7/3.1.0.0-78 HDP-GPL/centos7/3.x/updates/3.1.0.0

tar xvzf ${SRC}/HDP-UTILS-1.1.0.22-centos7.tar.gz
mkdir -p HDP-UTILS-1.1.0.22/repos
mv HDP-UTILS/centos7/1.1.0.22 HDP-UTILS-1.1.0.22/repos/centos7

tar xvzf ${SRC}/HDP-3.1.0.0-centos7-rpm.tar.gz
mkdir -p HDP/centos7/3.x/updates
mv HDP/centos7/3.1.0.0-78 HDP/centos7/3.x/updates/3.1.0.0

```



# HDP 3.1

## Services from hdp2.6.5

- Remove SLIDER, HCAT, WEBHCAT_SERVER, SPARK_CLIENT, SPARK_JOBHISTORYSERVER

- Add YARN_REGISTRY_DNS,TIMELINE_READER (On namnode or runnode)

There is no choices to add another YARN_REGISTRY_DNS using Ambari.
Another TIMELINE_READER can be added later with Ambari. But when building with two instances, it failed.


# TODO

- Postgresql DRP compliance
- Postgresql 9.6 or 10.2
- HDFS Rack awarness
- Kafka Rack awarness
- Securing
- Test DRP
- Setup Ranger admin HA.
- Check Timeline service 2.0
- Passage en openjdk.



