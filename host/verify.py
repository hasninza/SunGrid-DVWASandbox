#!/usr/bin/env python3
"""Verify the local SunGrid DVWA VirtualBox VM and its Host-Only web endpoint.

Run on the Windows host:
  python host\verify.py --vm SunGrid-DVWA-VM --ip 192.168.56.10
This script reports observed facts only. It does not change VM configuration.
"""
import argparse
import shutil
import subprocess
import sys
import urllib.error
import urllib.request


def run_vbox(args):
    return subprocess.run(
        ["VBoxManage", *args],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )


def main():
    parser = argparse.ArgumentParser(description="Verify SunGrid DVWA lab")
    parser.add_argument("--vm", required=True, help="VirtualBox VM name")
    parser.add_argument("--ip", required=True, help="Guest Host-Only IPv4 address")
    args = parser.parse_args()

    failures = 0
    print("SunGrid DVWA host verification")
    print(f"Target VM: {args.vm}")
    print(f"Guest IP:  {args.ip}")
    print("-" * 40)

    vbox = shutil.which("VBoxManage")
    if not vbox:
        print("[FAIL] VBoxManage not found. Install VirtualBox or add its folder to PATH.")
        return 2
    print(f"[PASS] VBoxManage found: {vbox}")

    listing = run_vbox(["list", "vms"])
    if listing.returncode != 0:
        print("[FAIL] Could not list VirtualBox VMs.")
        print((listing.stderr or listing.stdout).strip())
        return 2
    vm_exists = any(args.vm.lower() in line.lower() for line in listing.stdout.splitlines())
    if not vm_exists:
        print(f"[FAIL] VM not found: {args.vm}")
        failures += 1
    else:
        print(f"[PASS] VM exists: {args.vm}")

    info = run_vbox(["showvminfo", args.vm, "--machinereadable"])
    if info.returncode != 0:
        print("[FAIL] Could not read VM information. Check the VM name.")
        print((info.stderr or info.stdout).strip())
        return 2

    values = {}
    for line in info.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"')

    state = values.get("VMState", "unknown")
    if state == "running":
        print(f"[PASS] VM state: {state}")
    else:
        print(f"[FAIL] VM state: {state} (VM must be running for live checks)")
        failures += 1

    host_only = [
        (key, value) for key, value in values.items()
        if key.startswith("hostonlyadapter") and value
    ]
    nic_types = [
        (key, value) for key, value in values.items()
        if key.startswith("nic") and value
    ]
    if host_only and any(value.lower() == "hostonly" for _, value in nic_types):
        print("[PASS] Host-Only adapter configured: " + ", ".join(v for _, v in host_only))
    else:
        print("[FAIL] No Host-Only adapter was confirmed in VirtualBox settings.")
        print("       NIC settings: " + (", ".join(f"{k}={v}" for k, v in nic_types) or "not reported"))
        failures += 1

    url = f"http://{args.ip}/dvwa/login.php"
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "SunGrid-Lab-Verifier/1.0"})
        with urllib.request.urlopen(request, timeout=8) as response:
            print(f"[PASS] DVWA HTTP endpoint responded: {url} (HTTP {response.status})")
    except urllib.error.HTTPError as exc:
        print(f"[FAIL] DVWA endpoint returned HTTP {exc.code}: {url}")
        failures += 1
    except Exception as exc:
        print(f"[FAIL] DVWA endpoint not reachable: {url} ({exc})")
        failures += 1

    print("-" * 40)
    if failures:
        print(f"RESULT: NOT VERIFIED ({failures} check(s) failed)")
        return 1
    print("RESULT: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.TimeoutExpired:
        print("[FAIL] VirtualBox command timed out.")
        sys.exit(2)
