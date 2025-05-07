FROM ubuntu:22.04 AS base
WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt-cache \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=apt-lib \
    sed -i "s/archive.ubuntu.com/mirror.kakao.com/g" /etc/apt/sources.list &&\
    apt-get update

FROM base AS builder

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt-cache \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=apt-lib \
    apt-get install -y curl build-essential

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

COPY Cargo.lock .
COPY Cargo.toml .
COPY src src

RUN --mount=type=cache,target=/root/.cargo/registry,sharing=locked,id=cargo-registry \
    --mount=type=cache,target=/root/.cargo/git,sharing=locked,id=cargo-git \
    cargo build --release

FROM base AS runner

COPY --from=builder /app/target/release/backend /app/

RUN echo 'ctf - nproc 1500' >> /etc/security/limits.conf && \
    useradd -U ctf && \
    chown -R root:ctf /app && \
    chmod -R 750 /app && \
    chmod +x /app/backend

USER ctf
CMD /app/backend
