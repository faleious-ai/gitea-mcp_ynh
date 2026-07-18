# AGENTS.md

## Mission

Maintain the YunoHost package for the official Gitea MCP server. The package tracks the newest stable upstream release that passes package and image validation. It must remain usable by ChatGPT, Codex and other Streamable HTTP MCP clients without storing a Gitea personal access token on the server.

## Read before changing

1. `manifest.toml`, `conf/image.env`, `tests.toml`, `scripts/` and `conf/`.
2. Official MCP source and release notes: https://gitea.com/gitea/gitea-mcp
3. Gitea API documentation: https://docs.gitea.com/development/api-usage
4. MCP transport specification: https://modelcontextprotocol.io/specification
5. Official image registry: https://hub.docker.com/r/gitea/gitea-mcp-server/tags
6. YunoHost packaging documentation: https://doc.yunohost.org/packaging_apps
7. Sibling packages:
   - https://github.com/faleious-ai/gitea_ynh
   - https://github.com/faleious-ai/gitea-runner_ynh

## Why the package uses an OCI digest

The official MCP project publishes a small multi-architecture image. Installing that image avoids shipping a Go toolchain and rebuilding upstream code on the user’s server. `conf/image.env` pins the official repository by immutable manifest-list digest. Tags such as `latest` are discovery metadata only and must never appear in the systemd runtime command.

The updater resolves a stable semantic-version tag, verifies that its manifest includes Linux amd64 and arm64 images, records the exact digest, updates the YunoHost package version, and leaves a reviewable diff.

## Authentication model

The server runs in Streamable HTTP mode. Each MCP client supplies a Gitea token in the `Authorization: Bearer` header. Nginx must forward that header unchanged. The package must not request, persist, log or inject a Gitea personal access token.

The YunoHost route is therefore reachable without portal authentication and hidden from the application tile. This is intentional: YunoHost SSO headers would not replace Gitea API authorization and could prevent remote MCP clients from connecting. Gitea remains the authorization authority and enforces the token scopes.

## Update policy

- Stable semantic versions only. Reject draft, RC, beta, alpha and nightly tags.
- Use only `docker.io/gitea/gitea-mcp-server`.
- Pin `repository@sha256:digest`; never execute a mutable tag.
- Do not publish an update until the image exists for every architecture declared in `manifest.toml`.
- Major versions require explicit review of transport, command-line and authentication changes.

## Required validation

```bash
python3 tools/validate_package.py
python3 -m py_compile tools/*.py
for script in scripts/*; do bash -n "$script"; done
docker manifest inspect "$(sed -n 's/^GITEA_MCP_IMAGE=//p' conf/image.env)"
```

Lifecycle validation must cover install, service startup, authenticated `initialize` and `tools/list`, unauthenticated rejection, upgrade, backup/restore, removal and correct operation through the configured YunoHost path. Do not claim CI or protocol success without evidence tied to an exact commit.

## Automation

- `tools/update_upstream.py` resolves the newest stable official image and immutable digest.
- `.github/workflows/upstream-update.yml` runs scheduled and manual updates.
- `.github/workflows/package-ci.yml` validates package files and the pinned image.
- Generated README files, once created by YunoHost tooling, must not be edited manually.

## Security rules

- Never commit or echo tokens.
- Preserve the `Authorization` header at the proxy.
- Keep proxy buffering disabled for streaming responses.
- Keep the container read-only and non-root as provided by upstream.
- Do not add arbitrary Docker socket mounts, host filesystem mounts or privileged mode.
- When upstream changes its HTTP authentication model, stop automated publication until the package and tests are explicitly adapted.
