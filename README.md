# SunGrid-DVWA-Sandbox

Automated, isolated Ubuntu Server 24.04 LTS + DVWA sandbox for SunGrid Solar Task 1: Vulnerability Assessment and Hardening of the SunGrid Solar Internal Portal.

This repository creates a local Oracle VirtualBox virtual machine, installs Damn Vulnerable Web Application (DVWA), verifies the deployment, captures a clean baseline snapshot, and generates evidence from the actual VirtualBox and network state.

**Important:** DVWA is intentionally vulnerable. It must remain on a Host-Only network and must never be exposed to the Internet, a corporate network, or a physical LAN.

## Objectives

- Create an isolated Ubuntu Server virtual machine using Oracle VirtualBox.
- Deploy DVWA from the official repository.
- Restrict access to the Host-Only subnet.
- Verify Apache, MariaDB, PHP, DVWA, firewall, and HTTP availability.
- Create a non-destructive clean-baseline snapshot.
- Generate a PDF and JSON evidence report using collected system facts only.

## Architecture

```text
Windows host
  +-- Oracle VirtualBox
        +-- SunGrid-DVWA-VM (Ubuntu Server)
              +-- Apache2 / PHP / MariaDB
              +-- DVWA web application
              +-- UFW restricted to Host-Only subnet
  +-- Host-Only adapter (isolated host-to-guest network)
```

The VM uses a Host-Only adapter for final operation. NAT may be used temporarily during Ubuntu installation or package downloads, then removed before final verification.

## Prerequisites

- Windows 10/11 with administrator privileges for VirtualBox host-only adapter operations.
- Oracle VirtualBox 7.x.
- Python 3.10 or newer.
- Internet access only for the initial Ubuntu ISO download and guest package installation.
- Approximately 25 GB free disk space.
- A terminal with `python` available on `PATH`.

## Repository layout

```text
SunGrid-DVWA-Sandbox/
├── Build.cmd
├── README.md
├── host/
│   ├── build.py
│   ├── Verify.cmd
│   ├── verify.py
│   ├── Snapshot.cmd
│   ├── snapshot.py
│   ├── GenerateEvidence.cmd
│   └── evidence.py
├── guest/
│   ├── install-dvwa.sh
│   └── verify-guest.sh
├── docs/
│   ├── task1-baseline.md
│   ├── ubuntu-install.md
│   └── troubleshooting.md
├── review/
│   └── scope-and-safety.md
├── config/
│   └── settings.json
└── evidence/
    └── README.md
```

## Quick start

### 1. Build the VM

```bat
Build.cmd
```

The builder:

- Checks for Python and VirtualBox.
- Downloads the official Ubuntu Server ISO if it is not already present.
- Creates a new VM named `SunGrid-DVWA-VM`.
- Configures 2048 MB RAM, 2 CPUs, and a 25 GB dynamically allocated disk.
- Configures a Host-Only network adapter.
- Attaches the Ubuntu ISO.
- Starts the VM for manual Ubuntu installation.

It does **not** delete or modify existing VMs, disks, or snapshots.

### 2. Install Ubuntu Server

Follow `docs/ubuntu-install.md`. During installation:

- Select the Host-Only adapter as the primary network interface if it receives an address.
- Create a local administrator account.
- Install OpenSSH server.
- Do not enable third-party drivers or automatic security updates if you want a stable lab baseline.

### 3. Install DVWA

From the Ubuntu guest, transfer and run:

```bash
sudo bash install-dvwa.sh
```

The script installs Apache, PHP, MariaDB, Git, required PHP modules, clones DVWA, creates its database, configures Apache, and restricts UFW access to the detected Host-Only subnet.

### 4. Verify from the guest

```bash
sudo bash verify-guest.sh
```

### 5. Verify from Windows

After the VM is running and you know its Host-Only IP address:

```bat
host\Verify.cmd --vm SunGrid-DVWA-VM --ip 192.168.56.10
```

Replace `192.168.56.10` with the actual guest IP address.

### 6. Snapshot the clean baseline

```bat
host\Snapshot.cmd --vm SunGrid-DVWA-VM
```

This creates `SunGrid-DVWA-Clean-Baseline`. It refuses to overwrite an existing snapshot.

### 7. Generate evidence

```bat
host\GenerateEvidence.cmd --vm SunGrid-DVWA-VM --ip 192.168.56.10
```

Outputs:

```text
evidence\SunGrid-DVWA-Evidence-YYYYMMDD-HHMMSS.json
evidence\SunGrid-DVWA-Evidence-YYYYMMDD-HHMMSS.pdf
```

The report contains only facts collected from VirtualBox, the guest IP, HTTP response, and checks actually run. Unexecuted checks are marked `NOT VERIFIED`.

## Security rules

- Use Host-Only networking for the final lab.
- Never use Bridged networking.
- Do not expose DVWA to the Internet.
- Remove NAT before final verification if it was used temporarily.
- Use a strong, unique database password; the installer prompts for it and does not hard-code it.
- Do not run destructive commands without explicit confirmation.
- Do not scan, attack, or test systems outside the authorized VM.

## References

- Official DVWA repository: https://github.com/digininja/DVWA
- Oracle VirtualBox `VBoxManage` reference: https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/vboxmanage.html
- Ubuntu Server download: https://ubuntu.com/download/server
