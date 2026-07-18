# Gitea MCP administration

## Endpoint

The package exposes the official Gitea MCP server through the configured YunoHost URL using Streamable HTTP. The service itself listens only on the reserved local port; Nginx provides TLS and forwards streaming responses.

The URL is normally:

```text
https://<domain>/<path>/mcp
```

Confirm the exact MCP route with the upstream server version and `tools/list` during installation validation. The reverse proxy preserves the `Authorization` header and disables response buffering.

## Authentication

This package does not store a Gitea personal access token. Each MCP client must send its own Gitea token:

```text
Authorization: Bearer <gitea-token>
```

Create a dedicated token for each client and grant only the scopes required by that client. Gitea remains the authorization authority. Revoking the token immediately removes that client’s access without modifying the MCP package.

## Client validation

After installation, use an MCP inspector or client to perform:

1. unauthenticated request, which must be rejected;
2. `initialize` with a read-only Gitea token;
3. `tools/list`;
4. one read-only repository operation;
5. one reversible write with a restricted test token;
6. token revocation followed by a rejected request.

Do not use a production administrator token for package tests.

## Runtime image

The service uses the official multi-architecture image pinned by immutable digest in:

```text
/var/www/gitea-mcp/image.env
```

The systemd unit runs the container read-only, without privileged mode, host filesystem mounts or the Docker socket. The configured Gitea URL is passed to the official MCP process; credentials are supplied only by clients.

## Logs and health

```bash
systemctl status gitea-mcp
journalctl -u gitea-mcp --since today
docker inspect gitea-mcp
```

Logs must never contain bearer tokens. Before sharing diagnostics, redact request headers and URLs containing credentials.

## Upgrades

The scheduled updater discovers the highest stable semantic-version tag of the official image, requires Linux amd64 and arm64 manifests, and commits the exact manifest-list digest. Upgrade publication must stop when command-line flags, HTTP transport or authentication semantics change.
