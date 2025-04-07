ARG BUILD_FROM
FROM $BUILD_FROM

# Set environment
ENV LANG C.UTF-8

# Install dependencies
RUN apk add --no-cache jq python3 py3-pip curl

# Install bashio manually from GitHub (correct method)
RUN curl -sSL https://github.com/hassio-addons/bashio/archive/master.tar.gz | tar -xz \
    && mv bashio-master /usr/lib/bashio \
    && ln -s /usr/lib/bashio/bashio /usr/bin/bashio

# Copy your scripts and files
COPY run.sh /run.sh
COPY ble_discovery.py /ble_discovery.py
COPY btle_dashboard.yaml /btle_dashboard.yaml
COPY ble_input_text.yaml /ble_input_text.yaml

# Make the script executable
RUN chmod a+x /run.sh

# Entrypoint
CMD [ "/run.sh" ]
