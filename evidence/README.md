# Evidence checklist

Required genuine evidence:
- `snapshot.png`: VirtualBox Snapshot Manager with actual clean-baseline snapshot name and timestamp.
- `verification-output.txt`: full output from running the host verifier on the actual VM/IP.
- `host-only-network.png`: VM network settings visibly showing Host-Only mode.
- `dvwa-browser.png`: DVWA login page loaded from the guest Host-Only IP.

## Capture the missing files

1. Boot the DVWA VM in VirtualBox and confirm its Host-Only IP address.
2. On the host Windows machine, run the host verifier from the repository folder using the VM name and guest IP shown in your VM:
   `python host\\verify.py --vm <VM-NAME> --ip <GUEST-IP>`
3. Save the actual terminal output as `evidence/verification-output.txt`. Do not fabricate or edit the output to make checks pass.
4. Open `http://<GUEST-IP>/DVWA/login.php` in the host browser and save a screenshot as `evidence/dvwa-browser.png`.
5. Verify the screenshots and output correspond to the same running VM and IP before submitting.


Current repository files are `snapshot.png` and `VirtualBox DVWA Host-Only Lab Setup.png`. Review the latter to ensure it clearly shows the Host-Only adapter settings.

`verification-output.txt` and `dvwa-browser.png` remain missing until captured from the real VM. No simulated screenshots or invented terminal output should be submitted as real evidence.
