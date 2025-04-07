ARG BUILD_FROM
FROM $BUILD_FROM

# Set locale
ENV LANG C.UTF-8

# Install bashio, jq, Python, and pip
RUN apk add --no-cache \
    bashio \
    jq \
    python3 \
    py3-pip

# Copy add-on scripts and config files
COPY run.sh /run.sh
COPY ble_discovery.py /ble_discovery.py
COPY btle_dashboard.yaml /btle_dashboard.yaml
COPY ble_input_text.yaml /ble_input_text.yaml

# Make the startup script executable
RUN chmod a+x /run.sh

# Set entrypoint
CMD [ "/run.sh" ]
