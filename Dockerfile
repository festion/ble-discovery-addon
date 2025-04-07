ARG BUILD_FROM
FROM $BUILD_FROM

# Set environment
ENV LANG C.UTF-8

# Install dependencies
RUN apk add --no-cache jq python3 py3-pip curl

# Install bashio library
RUN mkdir -p /usr/lib/bashio \
 && curl -sSL https://raw.githubusercontent.com/hassio-addons/bashio/main/bashio.sh -o /usr/lib/bashio/bashio.sh

# Copy your scripts and files
COPY run.sh /run.sh
COPY ble_discovery.py /ble_discovery.py
COPY btle_dashboard.yaml /btle_dashboard.yaml
COPY ble_input_text.yaml /ble_input_text.yaml

# Make the script executable
RUN chmod a+x /run.sh

# Entrypoint
CMD [ "/run.sh" ]
