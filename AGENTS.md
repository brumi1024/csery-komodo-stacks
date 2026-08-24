# AGENTS.md

Start with `README.md` for the high-level picture.
This repo is intentionally small: Komodo-managed resources stay consolidated in `komodo.toml` for Resource Sync Managed Mode.

## Secrets

- Keep secret values out of Git; reference them in `komodo.toml` with generic Komodo secret placeholders.
- Secrets come from Core config `[secrets]` mounted at `/config/config.toml`, never from Resource Sync `[[variable]]` entries, and never as documented `KOMODO_SECRETS__...` environment variables.
- The Caddy DuckDNS token and subdomain are expected as `[[CADDY_DUCKDNS_TOKEN]]` and `[[DUCKDNS_SUBDOMAIN]]`.
- The ACME account email is a Core secret as `[[ACME_EMAIL]]`, not a `[[variable]]`: this repo is public, and Managed Mode would otherwise keep overwriting the live value with whatever is committed here.

## Stack Conventions

- Each stack lives under `services/<name>/` with a `docker-compose.yaml`; Komodo stacks and non-secret variables are defined in the root `komodo.toml`.
- Persistent host data belongs under `${CONFIG_DIR}/<stack>/...`.
- Caddy config that should trigger redeploys belongs under `services/caddy/config/`.
- Deploy through Komodo; a manual `docker compose up` on the target host bypasses Managed Mode.

## Ports

- Shared host ports live as non-secret variables in `komodo.toml`; reuse one before hardcoding a new host port in Compose.

## Related repositories

- `brumi1024/komodo-app-stacks` is the larger sibling for the main estate; conventions here deliberately stay simpler (one `komodo.toml`, Managed Mode).
- `brumi1024/homelab-infra` bootstraps the main estate's hosts with Ansible; this deployment is not in its inventory.
