# Scope and Safety

## Authorized scope

Testing is authorized only against the local SunGrid-DVWA-VM virtual machine created by this project.

Authorized targets:

- The Ubuntu Server guest VM.
- DVWA hosted on that VM.
- Apache, MariaDB, PHP, and UFW configurations on that VM.
- The Host-Only network between the Windows host and the VM.

## Prohibited scope

Do not test, scan, exploit, or interfere with:

- The Internet.
- Corporate or production networks.
- Physical LAN devices.
- Other VirtualBox VMs.
- Host operating systems.
- Any system not explicitly created for this task.

## Network isolation

- Final operation must use Host-Only networking.
- Bridged networking is prohibited.
- NAT is permitted only temporarily for initial package downloads and must be removed before final verification.
- UFW must allow inbound HTTP and SSH only from the detected Host-Only subnet.

## Data handling

- Do not store passwords in source control.
- Do not include real credentials, API keys, customer data, or production identifiers.
- Use only synthetic or DVWA-provided test data.

## Destructive actions

- Do not delete VMs, disks, snapshots, databases, or firewall rules without explicit authorization.
- The provided automation avoids overwriting existing snapshots and does not delete existing VirtualBox objects.

## Intended use

DVWA is intentionally vulnerable. Use it only for authorized learning, vulnerability assessment practice, and hardening validation within this isolated sandbox.
