# AGENTS.md

Start with `README.md` for the high-level picture. This repo is intentionally
small and should keep Komodo-managed resources consolidated in `komodo.toml`
for Resource Sync Managed Mode.

## Secrets

- Keep secret values out of Git.
- Reference secrets in `komodo.toml` with generic Komodo secret placeholders.
- Do not define secrets as Resource Sync `[[variable]]` entries.
- Do not document arbitrary `KOMODO_SECRETS__...` environment variables; use
  Core config `[secrets]` mounted at `/config/config.toml`.
- The Caddy DuckDNS token and subdomain are expected as
  `[[CADDY_DUCKDNS_TOKEN]]` and `[[DUCKDNS_SUBDOMAIN]]`.
- The ACME account email is a Core secret as `[[ACME_EMAIL]]`, not a
  `[[variable]]`. This repo is public, and Managed Mode would otherwise keep
  overwriting the live value with whatever is committed here.

## Stack Conventions

- Put each stack under `services/<name>/`.
- Each stack should include `docker-compose.yaml`.
- Define Komodo stacks and non-secret variables in the root `komodo.toml`.
- Persistent host data belongs under `${CONFIG_DIR}/<stack>/...`.
- Caddy config that should trigger redeploys belongs under
  `services/caddy/config/`.
- Do not manually run `docker compose up` on the target host for managed stacks;
  deploy through Komodo.

## Ports

- Shared host ports live as non-secret variables in `komodo.toml`.
- Do not hardcode new host ports in Compose if a shared variable fits.
