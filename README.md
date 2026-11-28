# SunGrid-DVWA-Sandbox

Isolated VirtualBox lab for SunGrid Solar Task 1: Vulnerability Assessment and Hardening of the SunGrid Solar Internal Portal. DVWA is intentionally vulnerable; use only in this isolated lab.

## Layout
- `host/verify.py`: Windows-host checks for VM state/network configuration and DVWA HTTP response.
- `host/Verify.cmd`: wrapper for the host verifier.
- `guest/install-dvwa.sh`: installs DVWA stack in Ubuntu guest and configures UFW.
- `guest/verify-guest.sh`: read-only local service/endpoint checks.
- `config/settings.json`: project VM/snapshot settings.
- `review/scope-and-safety.md`: authorization and safety boundaries.
- `evidence/`: genuine evidence screenshots and actual verification output.

## Host verification
On Windows, from the repository root, run with the actual VM Host-Only IP:
```powershell
python host\verify.py --vm SunGrid-DVWA-VM --ip <actual-guest-ip>
```
Save the complete real terminal output as `evidence/verification-output.txt`. Do not fabricate results.

## Guest verification
Inside the Ubuntu guest:
```bash
sudo bash guest/verify-guest.sh
```
This checks Apache/MariaDB active state, DVWA config existence, local login endpoint, and UFW status. It does not prove Host-Only isolation.

## Safety
Final network mode must be Host-Only. Bridged networking is prohibited. NAT may be used temporarily for setup downloads only and must be removed before final checks. Do not test external, corporate, physical LAN, host, or other VM targets. Do not commit secrets.
