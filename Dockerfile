# Pulled Jan 12, 2023
FROM python:3.8@sha256:a3e26c144eb58f9af20c971fe2d6112f1691859ca17a42be0f9f0951a85da5eb
WORKDIR /srv
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt && rm requirements.txt
COPY djang ./djang
WORKDIR /srv/djang
ENTRYPOINT ["/srv/djang/entrypoint.sh"]
