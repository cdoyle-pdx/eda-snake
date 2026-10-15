# The game is served through EDA's HttpProxy, which sets
#   default-src 'self'; frame-ancestors 'self'; form-action 'self';
# with no unsafe-inline. So the UI ships as three same-origin files rather than
# one self-contained HTML: index.html + snake.css + snake.js.
FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY ui/        /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080
