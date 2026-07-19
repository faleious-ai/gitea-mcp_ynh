# Validation status

Last architecture update: 2026-07-19.

## Final package state

- Package-code HEAD: `a663d270a782a947b486bb0c6796006165c385d1`.
- Final package version: `1.3.0~ynh2`.
- Runtime image: official `gitea/gitea-mcp-server@sha256:26cf7bd4ce9face39ed25f0ec82817b1dfdfe8e829240130bffdf353e336ec00`.
- The updater verifies stable semantic versions, Linux amd64/arm64 availability and immutable digests, rejects downgrades and reports `already-current 1.3.0 digest=sha256:26cf7bd4...` on its idempotence run.
- Both workflows use `actions/checkout@v7.0.0` and `actions/setup-python@v6.3.0`.

## Root cause and corrections

- A real YunoHost 12.1.40.1 ARM64 installation of `1.3.0~ynh1` failed with exit code 127 before pulling the OCI image because `scripts/install` called the removed `ynh_systemd_action` helper while preparing Docker.
- Inspection found the same obsolete service helper in install, upgrade, restore and removal, plus obsolete Nginx and systemd configuration helpers in install, upgrade and removal.
- Lifecycle scripts now use YunoHost helpers 2.1: `ynh_systemctl`, `ynh_config_add_nginx`, `ynh_config_remove_nginx`, `ynh_config_add_systemd` and `ynh_config_remove_systemd`, with the current `--service=` argument.
- The package validator now scans every lifecycle script, rejects all five obsolete helper names and requires the current helpers in the relevant install, upgrade, restore and removal paths.
- The package revision advanced to `1.3.0~ynh2`; domain/path arguments, public MCP permission, port reservation, immutable image digest and ARM64/AMD64 declarations were preserved.
- The earlier OCI correction remains in place: the official image has no entrypoint, so the systemd service and smoke test explicitly invoke `/app/gitea-mcp`.

## Commands and evidence

Required static and image validation:

```text
python3 tools/validate_package.py
python3 -m py_compile tools/*.py
find scripts -maxdepth 1 -type f ! -name '*.sql' -print0 | sort -z | while IFS= read -r -d '' script; do echo "Checking ${script}"; bash -n "$script"; done
image="$(sed -n 's/^GITEA_MCP_IMAGE=//p' conf/image.env)"
docker manifest inspect "$image"
docker pull "$image"
docker image inspect "$image"
docker run --rm --read-only --tmpfs /tmp:rw,noexec,nosuid,size=32m "$image" /app/gitea-mcp --help
```

The previous exact static checks, OCI manifest/image checks, HTTP smoke test and package-linter procedure passed for `1.3.0~ynh1`. The `~ynh2` helper correction still requires final workflow results and a new real YunoHost installation attempt before lifecycle success can be claimed.

## Required before production use

On the real YunoHost 12 ARM64 host, install `1.3.0~ynh2` and confirm Docker startup, immutable image pull, Nginx/systemd deployment and service health. Then validate `/mcp`, unauthenticated rejection, authenticated `initialize`/`tools/list`/read/reversible-write, token revocation, upgrade, backup/restore, URL change, removal and reboot health. Confirm logs contain no Authorization values.

## Current classification

`YUNOHOST_HELPERS_CORRECTED_REINSTALL_REQUIRED`

Read `AGENTS.md` and `doc/ADMIN.md` before continuing.
