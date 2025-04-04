ARG BUILD_FROM
FROM $BUILD_FROM

# Debug information
RUN echo "Python version:" && python3 --version
RUN echo "Pip version:" && pip3 --version

# Try installing without upgrading pip
RUN pip3 install --no-cache-dir requests

# Copy root filesystem
COPY rootfs /

# Make scripts executable
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]