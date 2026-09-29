#!/bin/sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir -p "$SCRIPT_DIR/bin"
cc -O2 -Wall -Wextra -o "$SCRIPT_DIR/bin/mdio_write" "$SCRIPT_DIR/src/mdio_write.c"
cc -O2 -Wall -Wextra -o "$SCRIPT_DIR/bin/mdio_exp_read" "$SCRIPT_DIR/src/mdio_exp_read.c"
chmod +x "$SCRIPT_DIR/bin/mdio_write" "$SCRIPT_DIR/bin/mdio_exp_read"
printf '%s\n' "Built MDIO utilities in bin/."
