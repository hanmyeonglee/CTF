#!/bin/sh

RAND_STR=$(openssl rand -hex 16)
SECRET_PATH=$(echo "${RAND_STR}" | fold -w1 | paste -sd"/")
SECRET=$(openssl rand -base64 32 | tr -dc 'A-Z' | head -c 3)

iptables -P OUTPUT DROP
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A OUTPUT -p tcp -d web --dport 5000 -j ACCEPT

SECRET_PATH="/app/${SECRET_PATH}"
mkdir -p "${SECRET_PATH}"
echo "${SECRET}" > "${SECRET_PATH}/secret"

chown -R ctf:ctf /app/users
chmod 440 "${SECRET_PATH}/secret"
su ctf

python3 /app/app.py "${SECRET_PATH}/secret"