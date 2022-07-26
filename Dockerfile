FROM python:3.8.12 as base


ADD https://git.iwoca.co.uk/devops/ci/raw/0.0.2/config/pip.conf /root/.config/pip/

WORKDIR /app/
COPY . .

RUN pip install -U pip==20.3.* && \
    VERSION=0.0.0test pip install -e .[test]
