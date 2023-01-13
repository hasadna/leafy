FROM leafy
RUN DJANGO_STATIC_ROOT=/srv/static python manage.py collectstatic --noinput -c
# Pulled Jan 12, 2023
FROM nginx@sha256:b8f2383a95879e1ae064940d9a200f67a6c79e710ed82ac42263397367e7cc4e
COPY --from=0 /srv/static /usr/share/nginx/html/static
RUN rm /usr/share/nginx/html/*.html
