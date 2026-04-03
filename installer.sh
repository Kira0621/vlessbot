#!/bin/bash

DOMAIN=$1
UUID=$(cat /proc/sys/kernel/random/uuid)

set -e

echo "[1] Install packages..."
apt update -y
apt install nginx certbot curl -y

echo "[2] Fake site..."
mkdir -p /var/www/html
cat > /var/www/html/index.html <<EOF
<!DOCTYPE html>
<html>
<head><title>Burmesestyles</title></head>
<body>
<h1>Welcome to Burmesestyles</h1>
<p>This website is under maintenance.</p>
</body>
</html>
EOF

echo "[3] Start nginx on :80 only (for ACME)..."
cat > /etc/nginx/sites-enabled/default <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    root /var/www/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ =404;
    }
}
EOF

systemctl restart nginx

echo "[4] Get SSL cert (standalone)..."
systemctl stop nginx
certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN
systemctl start nginx

echo "[5] Install Xray..."
bash <(curl -Ls https://raw.githubusercontent.com/XTLS/Xray-install/main/install-release.sh)

echo "[6] Write FINAL nginx 443 TLS config (your style)..."
cat > /etc/nginx/sites-enabled/default <<EOF
server {
    listen 443 ssl;
    server_name $DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    root /var/www/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ =404;
    }

    location /assets {
        proxy_pass http://127.0.0.1:10000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }
}
EOF

systemctl restart nginx

echo "[7] Write Xray VLESS WS config..."
cat > /usr/local/etc/xray/config.json <<EOF
{
  "inbounds": [{
    "port": 10000,
    "protocol": "vless",
    "settings": {
      "clients": [{"id": "$UUID"}],
      "decryption": "none"
    },
    "streamSettings": {
      "network": "ws",
      "wsSettings": {"path": "/assets"}
    }
  }],
  "outbounds": [{"protocol": "freedom"}]
}
EOF

systemctl restart xray

echo "===================================="
echo "VLESS LINK"
echo "===================================="
echo "vless://$UUID@$DOMAIN:443?type=ws&security=tls&path=/assets#Burmesestyles"
