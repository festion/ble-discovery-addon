ARG BUILD_FROM
FROM $BUILD_FROM

# Install required system packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    gcc \
    musl-dev

# Install the requests package directly without upgrading pip
RUN pip3 install --no-cache-dir requests

# Copy root filesystem
COPY rootfs /

# Make scripts executable
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]