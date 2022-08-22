FROM alpine:3.16

ARG PyYAML_VER="5.4.1"

# Install base dependecies and tooling
RUN apk update; \
    apk add \
      openssl \
      gcc \
      musl-dev \
      libc-dev \
      libffi-dev \
      python3 \
      python3-dev \
      openssl-dev \
      cargo \
      py3-pip \
      make \
      cmake;

# Install base Python dependencies and cloud tools
RUN pip install \
      PyYAML==${PyYAML_VER} \
      jinja2 \
      requests \
      dynaconf \
      GitPython \
      hvac \
      PyGithub \
      argparse \
      --no-cache-dir

COPY scripts/ scripts/



