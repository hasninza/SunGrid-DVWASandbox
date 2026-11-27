#!/usr/bin/env python3
"""Verify the SunGrid DVWA sandbox from the Windows host.

Usage:
  python verify.py --vm SunGrid-DVWA-VM --ip 192.168.56.10
"""

import argparse
import http.client
import ipaddress
import json
import logging
import pathlib
import platform
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "settings.json"
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("sungrid-verify")


def run(command):
    return subprocess.run([str(c) for c in command], text=True, capture_output=True, check=False)


def load_settings():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def find_vboxmanage(settings):
    candidate = settings["virtualbox"]["vboxmanage_path"]
    if candidate and Path(candidate).exists():
        return candidate
    found = shutil.which("VBoxManage")
    if found:
        return found
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    path = Path(program_files) / "Oracle" / "VirtualBox" / "VBoxManage.exe"
    if path.exists():
        return str(path)
    raise FileNotFoundError("VBoxManage.exe not found.")


def check_vm(vboxmanage, vm_name):
    result = run([vboxmanage, "showvminfo", vm_name, "--machinereadable"])
    if result.returncode != 0:
        return "FAIL", f"VM '{vm_name}' does not exist."
    state = ""
    adapter = ""
    for line in result.stdout.splitlines():
        if line.startswith("VMState="):
            state = line.split("=", 1)[1].strip('"')
        if line.startswith("hostonlyadapter1="):
            adapter = line.split("=", 1)[1].strip('"')
    if state == "running" and adapter:
        return "PASS", f"VM is running; Host-Only adapter: {adapter}"
    if state == "running":
        return "WARNING", "VM is running but no Host-Only adapter was detected."
    return "FAIL", f"VM state is '{state}', not running."


def check_host_only_subnet(vboxmanage):
    result = run([vboxmanage, "list", "hostonlyifs"])
    if result.returncode != 0:
        return "FAIL", "Unable to list Host-Only adapters."
    if "Name:" not in result.stdout:
        return "FAIL", "No Host-Only adapter is configured."
    return "PASS", "At least one Host-Only adapter is configured."


def tcp_reachable(ip, port, timeout=3):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def check_ports(ip, settings):
    results = []
    for port in settings["verification"]["required_ports"]:
        status = "PASS" if tcp_reachable(ip, port) else "FAIL"
        results.append((status, f"TCP port {port} on {ip}"))
    return results


def http_status(ip, path="/"):
    try:
        connection = http.client.HTTPConnection(ip, 80, timeout=5)
        connection.request("GET", path)
        response = connection.getresponse()
        status = response.status
        connection.close()
        return status
    except OSError:
        return None


def main():
    parser = argparse.ArgumentParser(description="Verify SunGrid DVWA sandbox connectivity.")
    parser.add_argument("--vm", required=True)
    parser.add_argument("--ip", required=True)
    args = parser.parse_args()
    settings = load_settings()
    try:
        vboxmanage = find_vboxmanage(settings)
    except FileNotFoundError as exc:
        log.error(str(exc))
        return 2

    checks = []
    status, detail = check_vm(vboxmanage, args.vm)
    checks.append((status, "VirtualBox VM exists and is running", detail))
    status, detail = check_host_only_subnet(vboxmanage)
    checks.append((status, "Host-Only adapter configured", detail))

    try:
        ipaddress.ip_address(args.ip)
        checks.append(("PASS", "Guest IP address format", args.ip))
    except ValueError:
        checks.append(("FAIL", "Guest IP address format", f"Invalid IP: {args.ip}"))
        args.ip = ""

    if args.ip:
        for status, detail in check_ports(args.ip, settings):
            checks.append((status, "Required service port", detail))
        http = http_status(args.ip)
        if http == 200:
            checks.append(("PASS", "DVWA HTTP endpoint", f"http://{args.ip}/ returned HTTP 200"))
        elif http:
            checks.append(("WARNING", "DVWA HTTP endpoint", f"http://{args.ip}/ returned HTTP {http}"))
        else:
            checks.append(("FAIL", "DVWA HTTP endpoint", f"http://{args.ip}/ did not respond"))

    print("\nSunGrid DVWA Sandbox Verification")
    print("=" * 50)
    for status, name, detail in checks:
        print(f"[{status:^7}] {name}: {detail}")
    failed = any(status == "FAIL" for status, _, _ in checks)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
