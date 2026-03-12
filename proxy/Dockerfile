# Stage 1: Build Caddy with the cache-handler plugin
FROM caddy:2.11.1-builder AS builder
RUN xcaddy build --with github.com/caddyserver/cache-handler

# Stage 2: Create the final image
FROM caddy:2.11.1
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
COPY . /etc/caddy/