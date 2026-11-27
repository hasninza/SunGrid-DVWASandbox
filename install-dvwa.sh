#!/usr/bin/env bash
# Install DVWA on Ubuntu Server for the isolated SunGrid Solar sandbox.
# Run as root: sudo bash install-dvwa.sh
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "ERROR: Run this script with sudo: sudo bash $0"
  exit 1
fi

read -r -s -p "Enter a strong MariaDB root password: " DB_ROOT_PASSWORD
echo
read -r -s -p "Enter a strong DVWA database password: " DVWA_DB_PASSWORD
echo

if [[ -z "$DB_ROOT_PASSWORD" || -z "$DVWA_DB_PASSWORD" ]]; then
  echo "ERROR: Passwords must not be empty."
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y apache2 mariadb-server php php-mysql php-gd php-xml php-mbstring php-curl git ufw

systemctl enable --now apache2 mariadb

DVWA_DIR=/var/www/html/DVWA
if [[ -d "$DVWA_DIR" ]]; then
  echo "WARNING: $DVWA_DIR already exists. No overwrite will occur."
else
  git clone https://github.com/digininja/DVWA.git "$DVWA_DIR"
fi

cd "$DVWA_DIR"
if [[ ! -f config/config.inc.php ]]; then
  cp config/config.inc.php.dist config/config.inc.php
fi

mysql -u root <<SQL
CREATE DATABASE IF NOT EXISTS dvwa;
CREATE USER IF NOT EXISTS 'dvwa'@'localhost' IDENTIFIED BY '${DVWA_DB_PASSWORD}';
ALTER USER 'dvwa'@'localhost' IDENTIFIED BY '${DVWA_DB_PASSWORD}';
GRANT ALL PRIVILEGES ON dvwa.* TO 'dvwa'@'localhost';
FLUSH PRIVILEGES;
SQL

mysql -u root -p"$DB_ROOT_PASSWORD" "$DVWA_DIR/database/dvwa.sql" 2>/dev/null || \
  mysql -u root -p"$DB_ROOT_PASSWORD" < "$DVWA_DIR/database/dvwa.sql"

chown -R www-data:www-data "$DVWA_DIR"
chmod -R 750 "$DVWA_DIR"
chmod 660 "$DVWA_DIR/config/config.inc.php"

HOSTONLY_SUBNET=""
for IP in $(hostname -I); do
  if [[ "$IP" == 192.168.56.* || "$IP" == 192.168.57.* || "$IP" == 192.168.58.* ]]; then
    HOSTONLY_SUBNET="${IP%.*}.0/24"
    break
  fi
done

if [[ -z "$HOSTONLY_SUBNET" ]]; then
  read -r -p "Enter the Host-Only subnet in CIDR form, for example 192.168.56.0/24: " HOSTONLY_SUBNET
fi

ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow from "$HOSTONLY_SUBNET" to any port 80 proto tcp
ufw allow from "$HOSTONLY_SUBNET" to any port 22 proto tcp
ufw --force enable

systemctl restart apache2

echo
echo "DVWA installation complete."
echo "URL: http://$(hostname -I | awk '{print $1}')/DVWA/"
echo "First-time setup: http://$(hostname -I | awk '{print $1}')/DVWA/setup.php"
echo "Firewall is restricted to: $HOSTONLY_SUBNET"
