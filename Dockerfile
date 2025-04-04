ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python and required packages
RUN apk update && \
    apk add --no-cache \
    python3 \
    py3-pip

# Debug information
RUN echo "Python version:" && python3 --version
RUN echo "Pip version:" && pip3 --version

# Try installing the needed package
RUN pip3 install requests

# Copy root filesystem
COPY rootfs /

# Make scripts executable
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]