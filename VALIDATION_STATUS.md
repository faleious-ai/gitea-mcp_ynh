# Validation status

Last architecture update: 2026-07-19.

## Final package state

- Package-code HEAD: `2cb4fa087103ba2467588f63f663bec922921841`.
- Final package version: `1.3.0~ynh3`.
- Runtime image: official `gitea/gitea-mcp-server@sha256:26cf7bd4ce9face39ed25f0ec82817b1dfdfe8e829240130bffdf353e336ec00`.
- The updater verifies stable semantic versions, Linux amd64/arm64 availability and immutable digests, rejects downgrades and reports `already-current 1.3.0 digest=sha256:26cf7bd4...` on its idempotence run.
- Both workflows use `actions/checkout@v7.0.0` and `actions/setup-python@v6.3.0`.

## Root cause and corrections

- A real YunoHost 12.1.40.1 ARM64 installation of `1.3.0~ynh1` failed with exit code 127 because lifecycle scripts called removed YunoHost helpers. Revision `~ynh2` replaced them with helpers 2.1 and added validator coverage.
- The same real host then confirmed Docker startup, successful retrieval of the pinned ARM64 OCI image and correct digest reuse. The first image pull had failed because the host CA state was stale; reinstalling `ca-certificates` made the exact pinned pull succeed.
- Installation of `1.3.0~ynh2` subsequently reached Nginx deployment and failed while reloading Nginx. `conf/nginx.conf` declared `proxy_http_version 1.1` and also included `/etc/nginx/proxy_params_no_auth`, which already declares that directive. Nginx rejected the duplicate as a fatal configuration error.
- Revision `~ynh3` removes the redundant app-level directive. The shared YunoHost include remains responsible for proxy HTTP version, while the app template still forwards `Authorization`, disables proxy buffering/cache and keeps long streaming timeouts.
- The package validator now requires `proxy_params_no_auth` and rejects any explicit `proxy_http_version` declaration in the app template, preventing recurrence on YunoHost 12.
- The unrelated Nextcloud duplicate `wasm` MIME entry remains only an Nginx warning and did not cause this installation failure.

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

The previous exact static checks, OCI manifest/image checks, HTTP smoke test and package-linter procedure passed for `1.3.0~ynh1`. The real ARM64 host has now demonstrated helper compatibility through Nginx deployment and successful use of the pinned image. Revision `~ynh3` still requires workflow results and one more real installation attempt before full lifecycle success can be claimed.

## Required before production use

On the real YunoHost 12 ARM64 host, install `1.3.0~ynh3` and confirm Nginx reload, systemd service creation and service health. Then validate `/mcp`, unauthenticated rejection, authenticated `initialize`/`tools/list`/read/reversible-write, token revocation, upgrade, backup/restore, URL change, removal and reboot health. Confirm logs contain no Authorization values.

## Current classification

`YUNOHOST_NGINX_DUPLICATE_FIXED_REINSTALL_REQUIRED`

Read `AGENTS.md` and `doc/ADMIN.md` before continuing.
