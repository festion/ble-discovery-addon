ARG BUILD_FROM
FROM $BUILD_FROM

# Minimal test - just echo a message
RUN echo "Basic test - if this fails, there's a fundamental issue with the build environment"

# Copy root filesystem
COPY rootfs /

# Make scripts executable
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]