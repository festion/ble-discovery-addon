ARG BUILD_FROM=python:3.9-alpine # or any other alpine based image.
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