ARG BUILD_FROM
FROM $BUILD_FROM

# Install required system packages
RUN apk add --no-cache \
    python3 \
    py3-pip

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    uuid \
    requests

# Copy your script
COPY ble_discovery.py /
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]