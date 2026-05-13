# Csery Komodo Stacks

Komodo-managed stacks for `csery-nas`.

`komodo.toml` is the source of truth for Komodo resources and non-secret variables. Each stack lives under `services/<name>/docker-compose.yaml`. Secrets stay out of Git and are referenced from `komodo.toml` with Komodo secret placeholders.

## Stacks

- `caddy`: public reverse proxy and DuckDNS integration
- `immich`: photo and video management
- `minidlna`: DLNA media server
- `monitoring`: Beszel hub and agent
- `nextcloud`: Nextcloud with MySQL
- `servarr`: Sonarr, Radarr, qBittorrent, and Jackett

## Requirements

- Komodo 2.x
- Komodo server target named `Local`
- Resource Sync pointing at `komodo.toml`
- Host ports `80` and `443` free for Caddy
- `/media/photos` available for Immich uploads

## Required Secrets

Mount a Komodo Core config at `/config/config.toml` and define:

```toml
[secrets]
CADDY_DUCKDNS_TOKEN = "..."
DUCKDNS_SUBDOMAIN = "..."
NEXTCLOUD_MYSQL_PASSWORD = "..."
IMMICH_DB_PASSWORD = "..."
BESZEL_AGENT_KEY = "..."
BESZEL_AGENT_TOKEN = "..."
```

Do not put secrets in Resource Sync variables. This repo expects Core-mounted secrets from `/config/config.toml`.

## Deploy

1. Load the required secrets into Komodo Core.
2. Create or update the Resource Sync for `komodo.toml`.
3. Enable Managed Mode with `include_variables = true`.
4. Run the Resource Sync.
5. Deploy `caddy`, then deploy the remaining stacks in Komodo.

Do not manually run `docker compose up` on the target host for managed stacks.

## Update

1. Edit and push this repo.
2. Run the Resource Sync in Komodo.
3. Redeploy the affected stack if needed.

Caddy config changes under `services/caddy/config/` require a Caddy redeploy.

## Storage

- App state usually lives under `${CONFIG_DIR}/<stack>/...`
- Immich uploads live at `/media/photos`
- Servarr uses `/media` mounts for media and downloads

## Public Hosts

- `heimdall.<duckdns-subdomain>.duckdns.org`
- `beszel.<duckdns-subdomain>.duckdns.org`
- `immich.<duckdns-subdomain>.duckdns.org`
- `komodo.<duckdns-subdomain>.duckdns.org`
- `nextcloud.<duckdns-subdomain>.duckdns.org`
- `qbittorrent.<duckdns-subdomain>.duckdns.org`
- `radarr.<duckdns-subdomain>.duckdns.org`
- `sonarr.<duckdns-subdomain>.duckdns.org`
