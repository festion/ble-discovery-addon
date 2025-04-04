ARG BUILD_FROM
FROM $BUILD_FROM

# Install required system packages and Python dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    gcc \
    musl-dev \
    py3-requests

# Additional Python package installation with error handling
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir \
    requests \
    || (echo "pip install failed" && exit 1)

# Copy root filesystem
COPY rootfs /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]