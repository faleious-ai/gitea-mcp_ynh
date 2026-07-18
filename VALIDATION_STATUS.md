# Validation status

Last architecture update: 2026-07-18.

## Current package state

- Package pin: `1.3.0~ynh1`.
- Runtime image: official `gitea/gitea-mcp-server` multi-architecture image pinned by immutable manifest-list digest.
- Upstream v1.3.0 documents `-t http`, `--host`, `--port` and the Streamable HTTP route `/mcp`; the systemd and Nginx templates implement that contract.
- Streamable HTTP reverse proxy, Authorization forwarding, disabled proxy buffering and long streaming timeouts are configured.
- The package stores no Gitea personal access token; clients provide their own Bearer token.
- Install, upgrade, backup, restore, removal and URL-change scripts are present and executable.
- Static validation plus scheduled/manual update workflows are present.

## Required before production use

1. Install on disposable YunoHost 12 infrastructure.
2. Demonstrate service health and correct operation through the configured domain and path ending in `/mcp`.
3. Verify unauthenticated rejection.
4. With a disposable scoped Gitea token, demonstrate `initialize`, `tools/list`, one read operation and one reversible write.
5. Revoke the token and demonstrate rejection.
6. Test upgrade, backup/restore, URL change, removal and reboot health.
7. Confirm logs contain no Authorization values.
8. Record exact commit, workflow run and evidence.

## Current classification

`PACKAGE_IMPLEMENTED_PROTOCOL_STATICALLY_VERIFIED_LIFECYCLE_UNVERIFIED`

Read `AGENTS.md` and `doc/ADMIN.md` before continuing.
