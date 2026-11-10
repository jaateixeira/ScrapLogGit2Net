#!/bin/bash
# Source this file, then call `require_tools TOOL...` at the start of an acceptance
# test script. If a tool is missing, it says how to install it and exits with code 1,
# instead of letting the test fail halfway with "command not found".
#
# These are system programs, not Python packages: pip cannot install them, so they
# are not in requirements.txt or pyproject.toml.

require_tools() {
    local missing=0 tool
    for tool in "$@"; do
        if ! command -v "$tool" > /dev/null 2>&1; then
            case "$tool" in
                xmllint) echo "ERROR: xmllint not found. Install it with: sudo apt install libxml2-utils (Debian/Ubuntu), sudo dnf install libxml2 (Fedora) or brew install libxml2 (macOS)." >&2 ;;
                unzip)   echo "ERROR: unzip not found. Install it with: sudo apt install unzip (Debian/Ubuntu) or sudo dnf install unzip (Fedora)." >&2 ;;
                *)       echo "ERROR: $tool not found. Install it and run the test again." >&2 ;;
            esac
            missing=1
        fi
    done
    if [ "$missing" -ne 0 ]; then
        exit 1
    fi
}
