# CLI-only image for nd2_export.
# The GUI entrypoint depends on tkinter and is intentionally not exposed here;
# containerized use cases are batch conversion on servers / HPC.

FROM python:3.11-slim

# System deps kept minimal: tifffile and nd2 are pure-Python wheels on x86_64/arm64.
# build-essential is added only in the build stage in case a dep needs compilation,
# then discarded to keep the runtime image small.
FROM python:3.11-slim AS build
WORKDIR /build
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir --upgrade pip build \
    && python -m build --wheel --outdir /wheels

FROM python:3.11-slim
LABEL org.opencontainers.image.title="nd2_export" \
      org.opencontainers.image.description="Streaming ND2 to OME-TIFF exporter for large microscopy datasets" \
      org.opencontainers.image.source="https://github.com/foertsch/nd2_export" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /data

COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl \
    && rm -rf /wheels

# Default working directory /data is where users mount their ND2 folder:
#   docker run --rm -v "$PWD:/data" foertsch/nd2-export batch .
ENTRYPOINT ["nd2-export"]
CMD ["--help"]
