## Patch Ansible

End of helm generated manifest:

    ...
	---
	# Source: provisioner/templates/namespace.yaml
	
	
	---
	# Source: provisioner/templates/pod-security-policy.yaml


In virtualenv/lib/python2.7/site-packages/ansible/module_utils/k8s/raw.py

Around line 90


    def execute_module(self):
        changed = False
        results = []
        self.client = self.get_api_client()
        for definition in self.resource_definitions:
            kind = definition.get('kind', self.kind)
            search_kind = kind
            ...
            
            
    def execute_module(self):
        changed = False
        results = []
        self.client = self.get_api_client()
        for definition in self.resource_definitions:
            if definition is not None:
                kind = definition.get('kind', self.kind)
                search_kind = kind
                ...
            
            
            
            
            
            
            