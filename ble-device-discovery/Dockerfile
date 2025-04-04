ARG BUILD_FROM
FROM $BUILD_FROM

# Install required system packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    gcc \
    musl-dev

# Upgrade pip and install dependencies
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir \
    requests

# Copy root filesystem
COPY rootfs /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]