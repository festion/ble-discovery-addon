
FROM ghcr.io/hassio-addons/base:12.2.7

ENV LANG C.UTF-8

RUN apk add --no-cache jq python3 py3-pip curl

RUN mkdir -p /usr/lib/bashio \
 && curl -sSL https://raw.githubusercontent.com/hassio-addons/bashio/main/bashio.sh -o /usr/lib/bashio/bashio.sh

COPY run.sh /run.sh
COPY ble_discovery.py /ble_discovery.py
COPY btle_dashboard.yaml /btle_dashboard.yaml
COPY ble_input_text.yaml /ble_input_text.yaml

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
