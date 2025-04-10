
FROM ghcr.io/hassio-addons/base:12.2.7

ENV LANG C.UTF-8

RUN apk add --no-cache jq python3 py3-pip curl unzip

RUN mkdir -p /usr/lib/bashio \
 && curl -sSL https://github.com/hassio-addons/bashio/archive/refs/heads/main.zip -o /tmp/bashio.zip \
 && unzip /tmp/bashio.zip -d /tmp \
 && mv /tmp/bashio-main/lib/* /usr/lib/bashio/ \
 && rm -rf /tmp/bashio.zip /tmp/bashio-main

COPY run.sh /run.sh
COPY ble_discovery.py /ble_discovery.py
COPY btle_dashboard.yaml /btle_dashboard.yaml
COPY ble_input_text.yaml /ble_input_text.yaml

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
