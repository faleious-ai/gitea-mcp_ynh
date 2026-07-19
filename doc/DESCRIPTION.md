# Gitea MCP

Gitea MCP packages the official Gitea Model Context Protocol server as a
YunoHost application. It exposes the server through Streamable HTTP at the
configured application path, ending in `/mcp`.

The application connects to the Gitea URL supplied during installation. It
does not create, request, store or inject a Gitea personal access token. Each
MCP client must send its own `Authorization: Bearer` header, which Nginx
forwards unchanged to Gitea.

The package runs the official multi-architecture container image pinned by an
immutable OCI digest. The container runs without privileged mode, host mounts
or Docker socket access, and the service uses a read-only root filesystem with
only a temporary filesystem for `/tmp`.
