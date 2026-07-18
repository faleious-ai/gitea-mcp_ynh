#!/bin/bash

# This package intentionally stores no Gitea personal access token. In HTTP
# mode each MCP client supplies its own Bearer token and Gitea enforces scopes.

load_image_pin() {
    local pin_file="${1:-$install_dir/image.env}"
    # shellcheck disable=SC1090
    source "$pin_file"
    image="$GITEA_MCP_IMAGE"
}
