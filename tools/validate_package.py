#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(\d+\.\d+\.\d+)~ynh\d+$")
IMAGE = re.compile(r"^docker\.io/gitea/gitea-mcp-server@sha256:[0-9a-f]{64}$")
SYSTEMCTL = "ynh_systemctl"
NGINX_ADD = "ynh_config_add_nginx"
NGINX_REMOVE = "ynh_config_remove_nginx"
SYSTEMD_ADD = "ynh_config_add_systemd"
SYSTEMD_REMOVE = "ynh_config_remove_systemd"
OBSOLETE_HELPERS = {
    "ynh_systemd_action": SYSTEMCTL,
    "ynh_add_nginx_config": NGINX_ADD,
    "ynh_remove_nginx_config": NGINX_REMOVE,
    "ynh_add_systemd_config": SYSTEMD_ADD,
    "ynh_remove_systemd_config": SYSTEMD_REMOVE,
}


def read_env(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator:
            raise ValueError(f"invalid environment line: {raw_line}")
        result[key] = value
    return result


def main() -> int:
    errors: list[str] = []
    manifest = tomllib.loads((ROOT / "manifest.toml").read_text(encoding="utf-8"))
    tomllib.loads((ROOT / "tests.toml").read_text(encoding="utf-8"))
    env = read_env(ROOT / "conf/image.env")

    package_version = str(manifest.get("version", ""))
    match = SEMVER.fullmatch(package_version)
    if not match:
        errors.append(f"invalid package version: {package_version}")
    elif env.get("GITEA_MCP_VERSION") != match.group(1):
        errors.append("manifest and image version differ")

    image = env.get("GITEA_MCP_IMAGE", "")
    if not IMAGE.fullmatch(image):
        errors.append("image must be the official repository pinned by sha256 digest")
    if ":latest" in image or ":nightly" in image:
        errors.append("mutable image tag is forbidden")

    nginx = (ROOT / "conf/nginx.conf").read_text(encoding="utf-8")
    if "include proxy_params_no_auth;" not in nginx:
        errors.append("nginx must include YunoHost proxy_params_no_auth")
    if re.search(r"^\s*proxy_http_version\b", nginx, re.MULTILINE):
        errors.append(
            "nginx must not redeclare proxy_http_version already provided by proxy_params_no_auth"
        )
    if "Authorization $http_authorization" not in nginx:
        errors.append("nginx must preserve the Authorization header")
    if "proxy_buffering off" not in nginx:
        errors.append("nginx buffering must remain disabled for MCP streaming")
    if "__PORT_HTTP__" not in nginx:
        errors.append("nginx must use the named YunoHost HTTP port")

    service = (ROOT / "conf/systemd.service").read_text(encoding="utf-8")
    for required in (
        "__IMAGE__",
        "/app/gitea-mcp",
        "-t http",
        "--host __GITEA_URL__",
        "--port __PORT_HTTP__",
        "--read-only",
    ):
        if required not in service:
            errors.append(f"systemd service missing {required}")
    if "--privileged" in service or "/var/run/docker.sock" in service:
        errors.append("MCP container must not be privileged or mount the Docker socket")

    scripts: dict[str, str] = {}
    for script_path in (ROOT / "scripts").iterdir():
        if not script_path.is_file():
            continue
        script = script_path.read_text(encoding="utf-8")
        scripts[script_path.name] = script
        for obsolete, replacement in OBSOLETE_HELPERS.items():
            if obsolete in script:
                errors.append(
                    f"scripts/{script_path.name} uses obsolete {obsolete}; use {replacement}"
                )
        if b"\r\n" in script_path.read_bytes():
            errors.append(f"CRLF line endings in {script_path.relative_to(ROOT)}")

    for lifecycle in ("install", "upgrade"):
        script = scripts[lifecycle]
        for required in (SYSTEMCTL, NGINX_ADD, SYSTEMD_ADD):
            if required not in script:
                errors.append(f"{lifecycle} must use {required}")

    restore_script = scripts["restore"]
    if SYSTEMCTL not in restore_script:
        errors.append("restore must use ynh_systemctl")

    remove_script = scripts["remove"]
    for required in (SYSTEMCTL, NGINX_REMOVE, SYSTEMD_REMOVE):
        if required not in remove_script:
            errors.append(f"remove must use {required}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"package-valid version={package_version} image={image}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
