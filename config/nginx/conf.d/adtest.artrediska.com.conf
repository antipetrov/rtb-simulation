server {
    listen 80;
    listen 443;

    server_name adtest.artrediska.com
    charset     utf-8;

    gzip on;
    gzip_disable "msie6";

    location /static/ {
        root /opt/;
    }

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Server $host;
        proxy_set_header Host $host;
        proxy_pass http://backend:8000;
    }
}