# Validation status

Last architecture update: 2026-07-19.

## Current package state

- Package pin: `1.3.0~ynh1`.
- Runtime image: official `gitea/gitea-mcp-server` multi-architecture image pinned by immutable manifest-list digest.
- Updater hardening was published at commit `7c4cf8d4077decd2300c23e336ae63871aece053`.
- The updater paginates the official registry tag list, accepts stable semantic versions only, verifies Linux amd64 and arm64 availability, rejects automated downgrades and stops for manual review if a current stable tag changes digest.
- Upstream v1.3.0 documents `-t http`, `--host`, `--port` and the Streamable HTTP route `/mcp`; the systemd and Nginx templates implement that contract.
- Streamable HTTP reverse proxy, Authorization forwarding, disabled proxy buffering and long streaming timeouts are configured.
- The package stores no Gitea personal access token; clients provide their own Bearer token.
- Install, upgrade, backup, restore, removal and URL-change scripts are present and executable.
- Static validation plus scheduled/manual/push-triggered update workflows are present.
- No lifecycle validation run tied to the hardened updater commit has been recorded.

## Required before production use

1. Confirm GitHub Actions is enabled and run package validation on the exact head.
2. Install on disposable YunoHost 12 infrastructure.
3. Demonstrate service health and correct operation through the configured domain and path ending in `/mcp`.
4. Verify unauthenticated rejection.
5. With a disposable scoped Gitea token, demonstrate `initialize`, `tools/list`, one read operation and one reversible write.
6. Revoke the token and demonstrate rejection.
7. Test upgrade, backup/restore, URL change, removal and reboot health.
8. Confirm logs contain no Authorization values.
9. Record exact commit, workflow run and evidence.

## Current classification

`UPSTREAM_CURRENT_AUTOMATION_HARDENED_PROTOCOL_STATICALLY_VERIFIED_LIFECYCLE_UNVERIFIED`

Read `AGENTS.md` and `doc/ADMIN.md` before continuing.
