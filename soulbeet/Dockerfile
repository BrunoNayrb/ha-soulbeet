FROM docccccc/soulbeet:master-full

ARG BUILD_ARCH
ARG BUILD_VERSION

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="addon" \
    io.hass.arch="${BUILD_ARCH}"

COPY run.py /run.py

ENTRYPOINT ["/usr/bin/python3", "/run.py"]
