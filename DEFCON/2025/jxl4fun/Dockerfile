FROM ubuntu:24.04@sha256:72297848456d5d37d1262630108ab308d3e9ec7ed1c3286a32fe09856619a782 as base

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libgif-dev \
    libz-dev \
    libopenexr-dev \
    libbrotli-dev \
    libgcc-10-dev

from base as runner

RUN apt-get update && apt-get install -y python3

WORKDIR /libjxl/lib

COPY ./libjxl/lib/ /libjxl/lib/
COPY ./libjxl/bin/ /libjxl/bin/

ENV LD_LIBRARY_PATH=/libjxl/lib:$LD_LIBRARY_PATH

WORKDIR /libjxl/bin