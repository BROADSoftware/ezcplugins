

## Security group parameters

A tag "Name" will be set from the SG name.

Rules parameters:

- protocol: ALL, TCP, UDP, ICMP, or the [protocol number](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)

- port: SSH, FTP, HTTP, ... Or a simple port number.

- from_port, to_port: Allow port range definition. Exclusive from "port"

- source/destination: May be:
  - "ANY"
  - "VPC"
  - "SELF"
  - A string, interpreted as a security group name (Already existing, or part of this definition. Beware of cyclic references).
  - A CIDR blocks
  