# Validation status

Last architecture update: 2026-07-18.

## Current package state

- Package pin: `1.3.0~ynh1`.
- Runtime image: official `gitea/gitea-mcp-server` multi-architecture image pinned by immutable manifest-list digest.
- Streamable HTTP reverse proxy, Authorization forwarding, disabled proxy buffering and long streaming timeouts are configured.
- The package stores no Gitea personal access token; clients provide their own Bearer token.
- Install, upgrade, backup, restore, removal and URL-change scripts are present and executable.
- Static validation plus scheduled/manual update workflows are present.

## Required before production use

1. Confirm the exact upstream HTTP command-line flags and effective MCP route on the pinned image.
2. Install on disposable YunoHost 12 infrastructure.
3. Demonstrate service health and correct operation through the configured domain and path.
4. Verify unauthenticated rejection.
5. With a disposable scoped Gitea token, demonstrate `initialize`, `tools/list`, one read operation and one reversible write.
6. Revoke the token and demonstrate rejection.
7. Test upgrade, backup/restore, URL change, removal and reboot health.
8. Confirm logs contain no Authorization values.
9. Record exact commit, workflow run and evidence.

## Current classification

`PACKAGE_IMPLEMENTED_PROTOCOL_AND_LIFECYCLE_UNVERIFIED`

Read `AGENTS.md` and `doc/ADMIN.md` before continuing.