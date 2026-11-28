#!/usr/bin/env bash
# Read-only checks for DVWA guest services and local web endpoint.
set -u
failures=0
echo "SunGrid DVWA guest verification"
if [ -r /etc/os-release ]; then . /etc/os-release; echo "OS: ${PRETTY_NAME:-unknown}"; fi
for svc in apache2 mariadb; do
  state=$(systemctl is-active "$svc" 2>/dev/null || true)
  if [ "$state" = active ]; then echo "[PASS] $svc active"; else echo "[FAIL] $svc state: $state"; failures=$((failures+1)); fi
done
if [ -f /var/www/html/DVWA/config/config.inc.php ]; then echo "[PASS] DVWA config exists"; else echo "[FAIL] DVWA config missing"; failures=$((failures+1)); fi
if curl --noproxy '*' -fsS --max-time 8 http://127.0.0.1/DVWA/login.php >/dev/null; then echo "[PASS] DVWA login endpoint responds locally"; else echo "[FAIL] DVWA login endpoint unavailable locally"; failures=$((failures+1)); fi
if command -v ufw >/dev/null 2>&1; then
  status=$(ufw status 2>/dev/null | head -1 || true); echo "UFW: $status"
  if echo "$status" | grep -qi active; then echo "[PASS] UFW active"; else echo "[WARN] UFW inactive; verify intended Host-Only restrictions"; fi
else echo "[WARN] UFW not installed"; fi
echo "Note: this guest script does not prove VirtualBox Host-Only isolation."
if [ "$failures" -gt 0 ]; then echo "RESULT: NOT VERIFIED ($failures failure(s))"; exit 1; fi
echo "RESULT: Local guest checks passed (Host-Only isolation not verified)"
