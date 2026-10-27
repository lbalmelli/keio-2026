FROM quay.io/jupyter/minimal-notebook:2026-07-28 AS jupyter-base

ARG OPENSYSML_KERNEL_VERSION=0.9.3.dev20261008
ARG OPENCODE_VERSION=1.19.4

ENV DEBIAN_FRONTEND=noninteractive \
    JUPYTER_ENABLE_LAB=yes \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER root

RUN apt-get update \
    && apt-get install --no-install-recommends --yes ca-certificates curl graphviz \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir \
        --requirement /tmp/requirements.txt \
        "jupyter-opensysml-kernel==${OPENSYSML_KERNEL_VERSION}" \
    && python -m jupyter kernelspec list \
    && test -d "$(python -c 'import sysconfig; print(sysconfig.get_path("data"))')/share/jupyter/kernels/sysml"

COPY opencode /opt/course/opencode
COPY .opencode /opt/course/.opencode
RUN touch /opt/course/.opencode/.gitignore
COPY docs/first_model.md /opt/course/docs/first_model.md
COPY docs/keio-logo.png /opt/course/docs/keio-logo.png

WORKDIR /home/jovyan/work

# Compose starts this image as root so the Jupyter Docker Stacks startup
# script can rename jovyan to NB_USER and then drop privileges.
USER root
ARG TARGETARCH
# OpenCode 1.19.4 ACP persona supports OpenCode >=1.0,<2. These release
# archives and SHA-256 digests are published for Linux amd64 and arm64.
RUN case "$TARGETARCH" in \
      amd64) artifact=x64-baseline; digest=1697ef40558d378bd2f72efa8fafe1bed1f0e664f09247b9357556b95dbc7cbc ;; \
      arm64) artifact=arm64; digest=8568230ccd847dc93e95b9f6894379077d3e014a16b48040743573e77c23e85f ;; \
      *) echo "Unsupported architecture: $TARGETARCH" >&2; exit 1 ;; \
    esac \
    && curl --fail --location --retry 3 "https://github.com/anomalyco/opencode/releases/download/v${OPENCODE_VERSION}/opencode-linux-${artifact}.tar.gz" -o /tmp/opencode.tar.gz \
    && echo "$digest  /tmp/opencode.tar.gz" | sha256sum --check - \
    && tar -xzf /tmp/opencode.tar.gz -C /usr/local/bin \
    && rm /tmp/opencode.tar.gz \
    && chmod 0755 /usr/local/bin/opencode

ENV HOME=/home/keio \
    XDG_DATA_HOME=/home/keio/state/data \
    XDG_CONFIG_HOME=/home/keio/state/config \
    XDG_CACHE_HOME=/home/keio/state/cache \
    XDG_STATE_HOME=/home/keio/state/state \
    OPENCODE_CONFIG=/opt/course/opencode/opencode.json \
    OPENCODE_CONFIG_DIR=/opt/course/.opencode \
    OPENCODE_DISABLE_AUTOUPDATE=true
