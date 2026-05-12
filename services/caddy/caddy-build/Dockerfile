ARG CADDY_VERSION=2.11.2

FROM caddy:${CADDY_VERSION}-builder-alpine AS builder

RUN xcaddy build \
    --with github.com/mholt/caddy-dynamicdns \
    --with github.com/caddy-dns/duckdns

FROM caddy:${CADDY_VERSION} AS caddy

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
