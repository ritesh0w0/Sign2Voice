#!/usr/bin/env bash
set -e

cat > /tmp/sign2voice.conf << 'EOF'
# Sign2Voice Isolated Configuration Snippet

location = /sign2voice {
    return 301 /sign2voice/;
}

location ^~ /sign2voice/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    client_max_body_size 10M;

    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
EOF

sudo mv /tmp/sign2voice.conf /etc/nginx/snippets/sign2voice.conf

if ! grep -q 'include /etc/nginx/snippets/sign2voice.conf;' /etc/nginx/sites-available/apidash; then
    sudo sed -i '/include \/etc\/nginx\/snippets\/trackflow.conf;/a \    include /etc/nginx/snippets/sign2voice.conf;' /etc/nginx/sites-available/apidash
fi

sudo nginx -t
sudo systemctl reload nginx
echo "NGINX_RELOAD_SUCCESS"

