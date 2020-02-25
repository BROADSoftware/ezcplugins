# AWS plugin

This plugin is intended to deploy cluster-based application on AWS cloud.

It will try to recreate a 'stable' environement, with controlled and well knownn instance name and IP. To achieve this, all instances are declared in private route53 zones.
  
This plugin create all instance with a Centos 7.X image. Note than all other plugins of ezcluster expect the same base OS.

## Requirement:

- AWS cli, Ansible and Terraform must be installed on the control node. And credential configured to access appropriate AWS account

- This plugin assume all instance will be on a single VPC. A VPC can host several clusters.

- Once VM are created, the control node must be able to access them using SSH. This can be achieved be setting up a VPN for VPC access.  For example, the one in AWS marketplace from [openvpn](https://aws.amazon.com/marketplace/pp/B00MI40CAE/ref=mkt_wir_openvpn_byol) (Free for up to 2 connected devices). 

- Two route53 zones must be defined and bound to the used VPC. One for forward resolution and one for the reverse. (vpcX and XXX.XXX.in-addr.arpa)

- All subnet referenced in the cluster definition file must be tagged with a name 

## Security group parameters

A tag "Name" will be set from the SG name.

Rules parameters:

- protocol: ALL, TCP, UDP, ICMP, or the [protocol number](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)

- port: SSH, FTP, HTTP, ... Or a simple port number.

- from_port, to_port: Allow port range definition. Exclusive from "port"

- source/destination: May be:

  - "_ANY_": Access is granted for whatever address 
  - "_VPC_": Access is granted for all this VPC.
  - "_SELF_": Access is granted for all intances defined in this security group.
  - A string, interpreted as a security group name (Already existing, or part of this definition. Beware of cyclic references).
  - A CIDR blocks
  
## NVME

There is a well known problem with EBS NVME device mapping on 'nitro' based instance. This problem has been solved on Amazon AMI instances be a specific script and a set of UDEV rules.

This plugin implements this feature all created instance, thus solving this issue (hopefully). 

Some links on this subject:
  
- https://kevinclosson.net/2018/02/21/a-word-about-amazon-ebs-volumes-presented-as-nvme-devices-on-c5-m5-instance-types/
- https://russell.ballestrini.net/aws-nvme-to-block-mapping/
- https://github.com/AerisCloud/ansible-disk

