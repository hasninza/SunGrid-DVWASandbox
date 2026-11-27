#!/usr/bin/env python3
"""Create a non-destructive clean-baseline VirtualBox snapshot.

Usage:
  python snapshot.py --vm SunGrid-DVWA-VM
"""

import argparse
import json
import logging
import os
import pathlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "settings.json"
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("sungrid-snapshot")


def run(command):
    return subprocess.run([str(c) for c in command], text=True, capture_output=True, check=False)


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


def snapshot_exists(vboxmanage, vm_name, snapshot_name):
    result = run([vboxmanage, "snapshot", vm_name, "list", "--machinereadable"])
    return snapshot_name in result.stdout


def main():
    parser = argparse.ArgumentParser(description="Create the SunGrid DVWA clean baseline snapshot.")
    parser.add_argument("--vm", required=True)
    args = parser.parse_args()
    settings = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    try:
        vboxmanage = find_vboxmanage(settings)
    except FileNotFoundError as exc:
        log.error(str(exc))
        return 2

    name = settings["snapshot"]["name"]
    description = settings["snapshot"]["description"]

    info = run([vboxmanage, "showvminfo", args.vm, "--machinereadable"])
    if info.returncode != 0:
        log.error("VM '%s' does not exist. No changes were made.", args.vm)
        return 1
    state = next((line.split("=", 1)[1].strip('"') for line in info.stdout.splitlines() if line.startswith("VMState=")), "")
    if state != "running":
        log.error("VM must be running before snapshot creation. Current state: %s", state or "unknown")
        return 1

    if snapshot_exists(vboxmanage, args.vm, name):
        log.error("Snapshot '%s' already exists. This tool will not overwrite it.", name)
        return 1

    result = run([vboxmanage, "snapshot", args.vm, "take", name, "--description", description])
    if result.returncode == 0:
        log.info("Snapshot created successfully: %s", name)
        return 0
    log.error("Snapshot creation failed:\n%s", result.stderr.strip() or result.stdout.strip())
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
