# Csery Komodo Stacks

Komodo 2.x stack definitions for services running on `csery-nas`.

This repo is intentionally small and follows Komodo's stack-per-service model
for Compose files. Managed Komodo resources live in the root `komodo.toml` file
so Resource Sync can manage stacks and non-secret variables from one place.
Secret values are referenced as Komodo Core secrets.

## Current Stacks

| Stack | Path | Description |
| --- | --- | --- |
| `caddy` | `services/caddy/` | Caddy reverse proxy with DuckDNS DDNS support |
| `monitoring` | `services/monitoring/` | Glances server monitoring |
| `nextcloud` | `services/nextcloud/` | Nextcloud with MySQL sidecar |
| `servarr` | `services/servarr/` | Sonarr, Radarr, qBittorrent, and Jackett |

The `caddy` stack runs the public reverse proxy and DuckDNS updater. It proxies
to host-published ports for apps that still publish directly on `csery-nas`.

## Requirements

- Komodo 2.x with a server target named `Local`
- This repository connected as a Komodo repo or resource sync source
- DuckDNS token and DuckDNS subdomain provided as Komodo Core secrets
- Existing app containers still publishing their current host ports
- Host ports `80` and `443` available for Caddy

Do not manually run `docker compose up` on the target host for these managed
stacks. Deploy and redeploy through Komodo.

## Setup

1. Create or confirm the Komodo server target named `Local`.
2. Mount a Komodo Core config file at `/config/config.toml` in the Core
   container.
3. Add the DuckDNS secrets to the mounted Core config file:

   ```toml
   [secrets]
   CADDY_DUCKDNS_TOKEN = "..."
   DUCKDNS_SUBDOMAIN = "..."
   NEXTCLOUD_MYSQL_PASSWORD = "..."
   ```

4. Restart Komodo Core so the mounted secrets are loaded.
5. Create a Resource Sync pointing at this repo and `komodo.toml`.
6. Enable Managed Mode on the Resource Sync if Komodo UI edits should commit
   back to this file.
7. Run the Resource Sync to create or update the stack and non-secret variables.
8. Replace `ACME_EMAIL` with the email address Caddy should use for ACME account
   registration.
9. Confirm the legacy app port variables match the ports currently published on
   `csery-nas`.
10. Confirm host ports `80` and `443` are free on `csery-nas`.
11. Deploy the `caddy` stack from Komodo.
12. Verify Caddy logs and each public hostname.

Example verification commands on the target host:

```bash
docker logs caddy --tail=100
curl -I https://heimdall.example.duckdns.org
curl -I https://nextcloud.example.duckdns.org
```

## Komodo Variables

### Shared Variables

These are defined in `komodo.toml` and referenced by stack config as
`[[VARIABLE_NAME]]`.

| Variable | Default | Required | Description |
| --- | --- | --- | --- |
| `TZ` | `Europe/Budapest` | Yes | Timezone for stacks that need one |
| `CONFIG_DIR` | `/docker` | Yes | Host directory for persistent container data |
| `LOGGING_DRIVER` | `local` | Yes | Docker logging driver |
| `PUID` | `1000` | Yes | Default LinuxServer.io user ID |
| `PGID` | `1000` | Yes | Default LinuxServer.io group ID |

### Caddy Variables

| Variable | Default | Required | Description |
| --- | --- | --- | --- |
| `CADDY_VERSION` | `2.11.2` | Yes | Caddy version used for the custom build |
| `CADDY_HOST_ALIAS` | `csery-nas` | Yes | Hostname Caddy uses to reach host-published legacy containers |
| `DUCKDNS_ZONE` | `duckdns.org` | Yes | DuckDNS zone used by the Caddy dynamic DNS plugin |
| `ACME_EMAIL` | `replace-me@example.com` | Yes | Email address used for ACME account registration |
| `PORT_CADDY_HTTP` | `80` | Yes | Host HTTP port published by Caddy |
| `PORT_CADDY_HTTPS` | `443` | Yes | Host HTTPS port published by Caddy, including UDP for HTTP/3 |
| `PORT_CADDY_ADMIN` | `2019` | Yes | Host port for the Caddy admin API |

### Caddy App Port Variables

Caddy proxies to host-published app ports, so these values must match the ports
exposed on `csery-nas`.

| Variable | Default | Public hostname |
| --- | --- | --- |
| `PORT_HEIMDALL_HTTP` | `10080` | `heimdall.<duckdns-subdomain>.duckdns.org` |
| `PORT_KOMODO_HTTP` | `9120` | `komodo.<duckdns-subdomain>.duckdns.org` |
| `PORT_NEXTCLOUD_HTTP` | `8082` | `nextcloud.<duckdns-subdomain>.duckdns.org` |
| `PORT_SONARR_HTTP` | `8989` | `sonarr.<duckdns-subdomain>.duckdns.org` |
| `PORT_QBITTORRENT_HTTP` | `8080` | `qbittorrent.<duckdns-subdomain>.duckdns.org` |
| `PORT_RADARR_HTTP` | `7878` | `radarr.<duckdns-subdomain>.duckdns.org` |

### Managed Stack Port Variables

| Variable | Default | Used by |
| --- | --- | --- |
| `PORT_JACKETT_HTTP` | `9117` | Jackett web UI |
| `PORT_QBITTORRENT_TORRENTING` | `57305` | qBittorrent TCP/UDP torrent port |
| `PORT_GLANCES_HTTP` | `61208` | Glances web UI |
| `PORT_GLANCES_API` | `61209` | Glances API |

### Secrets

| Secret reference | Required by | Description |
| --- | --- | --- |
| `[[CADDY_DUCKDNS_TOKEN]]` | `komodo.toml` | DuckDNS token passed into Caddy as `DUCKDNS_TOKEN` |
| `[[DUCKDNS_SUBDOMAIN]]` | `komodo.toml` | DuckDNS subdomain passed into Caddy as `DUCKDNS_SUBDOMAIN` |
| `[[NEXTCLOUD_MYSQL_PASSWORD]]` | `komodo.toml` | Existing password for the `nextcloud-user` MySQL account |

Keep secret values out of Git and out of Resource Sync-managed variables. Add
new stack secrets as Komodo Core secrets and reference them from `komodo.toml`
with `[[SECRET_NAME]]` placeholders.

Core secrets must be configured in Komodo Core config, not with arbitrary
`KOMODO_SECRETS__...` environment variables. Mount a config file to
`/config/config.toml` in the Core container and include:

```toml
[secrets]
CADDY_DUCKDNS_TOKEN = "..."
DUCKDNS_SUBDOMAIN = "..."
NEXTCLOUD_MYSQL_PASSWORD = "..."
```

## Stack Layout

New stacks should follow this layout:

```text
komodo.toml
services/<name>/
  docker-compose.yaml
```

Persistent host data should be mounted under `${CONFIG_DIR}/<stack>/...`.
Caddy config that should trigger redeploys belongs under
`services/caddy/config/` and should be listed in the relevant `komodo.toml`
stack's `config_files` with `requires = "Redeploy"`.

If a new stack needs a host port, add it as a non-secret variable in
`komodo.toml` when it is shared or likely to be referenced by more than one
stack. Avoid hardcoding new host ports directly in Compose when a shared
variable fits.

## Resource Sync

Use one Komodo Resource Sync pointing at `komodo.toml`. Keeping all synced
Komodo resources in a single file makes Managed Mode straightforward: Git
pushes update Komodo, and supported Komodo UI edits can be committed back into
the same file.

Set `include_variables = true` on the Resource Sync so Managed Mode writes the
non-secret `[[variable]]` entries back to `komodo.toml` instead of dropping
them during UI-to-Git commits.

Keep manual secrets out of `komodo.toml`; only reference them by placeholder.
