#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.toml"
IMAGE_ENV = ROOT / "conf/image.env"
API = "https://hub.docker.com/v2/repositories/gitea/gitea-mcp-server/tags?page_size=100&ordering=last_updated"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
REQUIRED = {("linux", "amd64"), ("linux", "arm64")}


def request_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "gitea-mcp-ynh-updater"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def version_key(value: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def replace_manifest_version(text: str, version: str) -> str:
    updated, count = re.subn(
        r'(?m)^(version\s*=\s*)"[^"]+"\s*$',
        rf'\1"{version}~ynh1"',
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError("manifest version not found")
    return updated


def main() -> int:
    data = request_json(API)
    stable = [item for item in data.get("results", []) if SEMVER.fullmatch(str(item.get("name", "")))]
    if not stable:
        raise RuntimeError("Docker Hub returned no stable semantic-version tags")
    release = max(stable, key=lambda item: version_key(str(item["name"])))
    version = str(release["name"])
    digest = str(release.get("digest", ""))
    if not DIGEST.fullmatch(digest):
        raise RuntimeError(f"invalid manifest-list digest for {version}: {digest}")

    available = {
        (str(image.get("os", "")), str(image.get("architecture", "")))
        for image in release.get("images", [])
        if str(image.get("status", "active")) == "active"
    }
    missing = REQUIRED - available
    if missing:
        raise RuntimeError(f"stable tag {version} lacks required platforms: {sorted(missing)}")

    env_text = IMAGE_ENV.read_text(encoding="utf-8")
    current_match = re.search(r"(?m)^GITEA_MCP_VERSION=(.+)$", env_text)
    if not current_match:
        raise RuntimeError("GITEA_MCP_VERSION not found")
    current = current_match.group(1).strip()
    if current == version:
        print(f"already-current {version}")
        return 0

    image = f"docker.io/gitea/gitea-mcp-server@{digest}"
    IMAGE_ENV.write_text(
        "# Updated only by tools/update_upstream.py after validating a stable multi-arch tag.\n"
        f"GITEA_MCP_VERSION={version}\n"
        f"GITEA_MCP_IMAGE={image}\n",
        encoding="utf-8",
    )
    manifest_text = MANIFEST.read_text(encoding="utf-8")
    MANIFEST.write_text(replace_manifest_version(manifest_text, version), encoding="utf-8")
    print(f"updated {current} -> {version} digest={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
