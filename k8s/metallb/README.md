
# PB:

The original file metallb.yaml ends with '---\n\n\n'. This confuse k8s ansible module, which fail on an empty definition (see lib.ansible.module_utils.k8s.raw.py, line 91)
This is why we define it as template, intead of fetching from Internet.
 
