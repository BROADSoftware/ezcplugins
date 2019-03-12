# Build 

- Tested with kubespray on this commit:

```
commit ccc3f89060b18b3532d6b054b15a7de10255671a (HEAD -> master, origin/master, origin/HEAD)
Author: Egor <iam@aylium.net>
Date:   Sun Oct 21 10:35:52 2018 +0300

    Add kube-router annotations (#3533)
```

- last tagged version (2.7.0) was not working in my context.

- Does not works with ansible 2.7. Use 2.6.3 (See release note on kubespray 2.7.0 release/tag)


# Access

https://m1.kspray4:6443/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/#!/login

To get a token, on m1, as root (Loaged as root, not by sudo)

kubectl -n kube-system get secret

kubectl -n kube-system describe secret namespace-controller-token-9w5j6
