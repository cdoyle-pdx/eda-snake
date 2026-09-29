# The game is one self-contained HTML file; nginx-unprivileged serves it on 8080
# and needs no root, no writable root filesystem, and no network egress.
FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY ui/index.html /usr/share/nginx/html/index.html
COPY nginx.conf   /etc/nginx/conf.d/default.conf

EXPOSE 8080
