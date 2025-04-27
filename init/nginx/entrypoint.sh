#!/bin/sh

echo "Creating NGINX config from template"
envsubst '${API_CONTAINER_NAME} ${API_PORT}' < /etc/nginx/templates/site.conf.template > /etc/nginx/conf.d/default.conf
chmod 444 /etc/nginx/conf.d/default.conf

echo "Starting NGINX"
nginx -g 'daemon off;'
