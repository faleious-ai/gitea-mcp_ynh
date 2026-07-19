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
PINNED_IMAGE = re.compile(r"^docker\.io/gitea/gitea-mcp-server@(sha256:[0-9a-f]{64})$")
REQUIRED = {("linux", "amd64"), ("linux", "arm64")}


def request_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "gitea-mcp-ynh-updater"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def all_tags() -> list[dict]:
    tags: list[dict] = []
    url: str | None = API
    pages = 0
    while url:
        pages += 1
        if pages > 20:
            raise RuntimeError("Docker Hub tag pagination exceeded safety limit")
        data = request_json(url)
        results = data.get("results", [])
        if not isinstance(results, list):
            raise RuntimeError("Docker Hub returned an invalid tag list")
        tags.extend(item for item in results if isinstance(item, dict))
        next_url = data.get("next")
        url = str(next_url) if next_url else None
    return tags


def version_key(value: str) -> tuple[int, int, int]:
    if not SEMVER.fullmatch(value):
        raise RuntimeError(f"invalid semantic version: {value!r}")
    major, minor, patch = value.split(".")
    return int(major), int(minor), int(patch)


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


def read_current_pin(text: str) -> tuple[str, str]:
    version_match = re.search(r"(?m)^GITEA_MCP_VERSION=(.+)$", text)
    image_match = re.search(r"(?m)^GITEA_MCP_IMAGE=(.+)$", text)
    if not version_match or not image_match:
        raise RuntimeError("GITEA_MCP_VERSION or GITEA_MCP_IMAGE not found")
    version = version_match.group(1).strip()
    version_key(version)
    image = image_match.group(1).strip()
    digest_match = PINNED_IMAGE.fullmatch(image)
    if not digest_match:
        raise RuntimeError(f"invalid pinned MCP image: {image}")
    return version, digest_match.group(1)


def main() -> int:
    stable = [item for item in all_tags() if SEMVER.fullmatch(str(item.get("name", "")))]
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
        if isinstance(image, dict) and str(image.get("status", "active")) == "active"
    }
    missing = REQUIRED - available
    if missing:
        raise RuntimeError(f"stable tag {version} lacks required platforms: {sorted(missing)}")

    env_text = IMAGE_ENV.read_text(encoding="utf-8")
    current, current_digest = read_current_pin(env_text)
    if version_key(current) > version_key(version):
        raise RuntimeError(f"refusing automated downgrade from {current} to {version}")
    if current == version:
        if current_digest != digest:
            raise RuntimeError(
                "the currently packaged stable tag now resolves to a different digest; "
                f"manual review required ({current_digest} -> {digest})"
            )
        print(f"already-current {version} digest={digest}")
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
