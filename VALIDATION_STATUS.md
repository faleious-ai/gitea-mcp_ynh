# Validation status

Last architecture update: 2026-07-19.

## Final package state

- Package-code HEAD: `3720fc3b1e66c48f5e893eec14c16334ff538447`.
- Final package version: `1.3.0~ynh1`.
- Runtime image: official `gitea/gitea-mcp-server@sha256:26cf7bd4ce9face39ed25f0ec82817b1dfdfe8e829240130bffdf353e336ec00`.
- The updater verifies stable semantic versions, Linux amd64/arm64 availability and immutable digests, rejects downgrades and reports `already-current 1.3.0 digest=sha256:26cf7bd4...` on its idempotence run.
- Both workflows use `actions/checkout@v7.0.0` and `actions/setup-python@v6.3.0`.

## Root cause and corrections

- The original smoke test ran `docker run <image> --help`. The official image has no entrypoint and its `Cmd` is `/app/gitea-mcp`; Docker therefore tried to execute `--help` and returned exit code 127. The test now asserts the OCI manifest and image contract, starts the pinned image with the explicit binary path and exercises the Streamable HTTP `/mcp` endpoint with a JSON-RPC `initialize` request.
- The systemd template now invokes `/app/gitea-mcp` explicitly and preserves HTTP host/port, host networking, read-only root filesystem, tmpfs and no Docker socket.
- Backup/restore now source the YunoHost common helper from the correct relative path. The Nginx template forwards Authorization and uses the standard no-auth proxy parameters. Upstream LICENSE and package description documentation were added.
- The official YunoHost package linter is executed in CI from a clean checkout and fails on real errors. It reports the fork's missing public catalog entry as the only accepted `AppCatalog.is_in_catalog` exception. The upstream `admindoc` warning is documented in `AGENTS.md` because upstream publishes the CLI/HTTP documentation in its repository README rather than a separate admin document.

## Commands and evidence

Local Windows checks used the bundled Python runtime and Git Bash because `python3`, Docker and a WSL distribution were unavailable:

```text
<bundled-python> -m py_compile tools/*.py
find scripts -maxdepth 1 -type f ! -name '*.sql' -print0 | sort -z | while IFS= read -r -d '' script; do echo "Checking ${script}"; bash -n "$script"; done
<bundled-python> tools/update_upstream.py
<bundled-python> tools/update_upstream.py   # idempotence: already-current 1.3.0
```

The exact static checks, OCI manifest/image checks, HTTP smoke test and package-linter procedure passed in the remote Linux workflows. No credential or Authorization value is stored by the package or test.

Validation runs for the package-code HEAD:

- Package validation: [run 29695451990](https://github.com/faleious-ai/gitea-mcp_ynh/actions/runs/29695451990).
- Update stable upstream release: [run 29695452793](https://github.com/faleious-ai/gitea-mcp_ynh/actions/runs/29695452793).

Both runs were green. The final package run logged `manifest-valid linux/amd64`, the expected non-root `/app` image contract and completion of the HTTP `initialize` smoke test. No Node.js 20 warning was present in the final logs.

## Required before production use

On disposable YunoHost 12 infrastructure, validate install, service health through `/mcp`, unauthenticated rejection, authenticated `initialize`/`tools/list`/read/reversible-write, token revocation, upgrade, backup/restore, URL change, removal and reboot health. Confirm logs contain no Authorization values.

## Current classification

`AUTOMATION_AND_PACKAGE_LINTER_VERIFIED_OCI_SMOKE_VERIFIED_LIFECYCLE_UNVERIFIED`

The lifecycle is intentionally not classified as verified because no YunoHost host was available in this workspace.

Read `AGENTS.md` and `doc/ADMIN.md` before continuing.
