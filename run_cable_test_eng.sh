#!/bin/sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON="$SCRIPT_DIR/.venv/bin/python3"
[ -x "$PYTHON" ] || PYTHON=python3
killall matchbox-keyboard squeekboard osk-wayland 2>/dev/null || true
exec "$PYTHON" "$SCRIPT_DIR/src/cable_test_eng.py"
