FROM nginx:latest

COPY ./letsencrypt/ /etc/letsencrypt/

COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./05-start.sh /docker-entrypoint.d/05-start.sh
