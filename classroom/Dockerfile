FROM python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258 AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /opt/course
COPY classroom/requirements.txt /tmp/classroom-requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/classroom-requirements.txt
COPY classroom /opt/course/classroom
# Docker COPY preserves source modes; some checkouts have tracked files at 0600.
# Keep application code root-owned and read-only to the unprivileged runtime user.
RUN chmod -R a+rX /opt/course/classroom
RUN useradd --create-home --uid 10001 classroom && mkdir /data /state && chown -R classroom:classroom /data /state
USER classroom

FROM runtime AS master
USER root
ARG OPENCODE_VERSION=1.19.4
ARG TARGETARCH
RUN apt-get update && apt-get install --no-install-recommends -y ca-certificates curl && rm -rf /var/lib/apt/lists/*
RUN case "$TARGETARCH" in \
      amd64) artifact=x64-baseline; digest=1697ef40558d378bd2f72efa8fafe1bed1f0e664f09247b9357556b95dbc7cbc ;; \
      arm64) artifact=arm64; digest=8568230ccd847dc93e95b9f6894379077d3e014a16b48040743573e77c23e85f ;; \
      *) exit 1 ;; esac \
    && curl --fail --location --retry 3 "https://github.com/anomalyco/opencode/releases/download/v${OPENCODE_VERSION}/opencode-linux-${artifact}.tar.gz" -o /tmp/opencode.tar.gz \
    && echo "$digest  /tmp/opencode.tar.gz" | sha256sum --check - \
    && tar -xzf /tmp/opencode.tar.gz -C /usr/local/bin \
    && rm /tmp/opencode.tar.gz
RUN mkdir -p /home/classroom/state && chown -R classroom:classroom /home/classroom/state
USER classroom
ENV HOME=/home/classroom OPENCODE_CONFIG=/opt/course/classroom/master-opencode.json CLASSROOM_TEACHER_URL=http://classroom-hub:8765 CLASSROOM_TEACHER_TOKEN_FILE=/data/teacher-token
