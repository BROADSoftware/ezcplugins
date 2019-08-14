# AWS plugin

## Requirement:

- terraform must be installed on the control node. And credential configured to access appropriate AWS account

- This plugin assume all VMs will be on a single VPC

- A VPC can host several clusters

- Once VM are created, the control node must be able to access them using SSH. This can be achieved be setting up a VPN for VPC access. See below

- A route53 root ('.') zone bound to our VPC.

### VPN access.

There is several solution to fullfil this need. For example, [openvpn](https://aws.amazon.com/marketplace/pp/B00MI40CAE/ref=mkt_wir_openvpn_byol) (Free for up to 2 connected devices). 

## Security group parameters

A tag "Name" will be set from the SG name.

Rules parameters:

- protocol: ALL, TCP, UDP, ICMP, or the [protocol number](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)

- port: SSH, FTP, HTTP, ... Or a simple port number.

- from_port, to_port: Allow port range definition. Exclusive from "port"

- source/destination: May be:
  - "_ANY_"
  - "_VPC_"
  - "_SELF_"
  - A string, interpreted as a security group name (Already existing, or part of this definition. Beware of cyclic references).
  - A CIDR blocks
  
  
  
## NVME
  
https://kevinclosson.net/2018/02/21/a-word-about-amazon-ebs-volumes-presented-as-nvme-devices-on-c5-m5-instance-types/

https://russell.ballestrini.net/aws-nvme-to-block-mapping/

https://github.com/AerisCloud/ansible-disk

### Scratchpad

ezcluster ../testebs.yml; ansible-playbook ./main.yml --tags hostname,selinux,resolv_conf,packages


yum install nvme-cli

Nitro:
ssh -i "aws_id1.pem" ec2-user@ip-172-30-2-253.ec2.internal


