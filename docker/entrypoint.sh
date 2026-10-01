#!/bin/sh
# Prepare /data, then run the app as an unprivileged user.
set -eu

CONFIG_DIR="${HISAABFLOW_CONFIG_DIR:-/data/configs}"
mkdir -p "$CONFIG_DIR"

# Add shipped configs the user doesn't have yet. Existing files are never
# overwritten, so edits made in ./data/configs survive upgrades.
for conf in /app/configs-default/*.conf; do
    target="$CONFIG_DIR/$(basename "$conf")"
    [ -e "$target" ] || cp "$conf" "$target"
done

if [ "$(id -u)" = "0" ]; then
    # Docker creates a missing ./data as root; hand it to the app user so the
    # files stay editable on the host (default uid/gid 1000).
    uid="${HISAABFLOW_UID:-1000}"
    gid="${HISAABFLOW_GID:-1000}"
    chown -R "$uid:$gid" /data
    exec setpriv --reuid="$uid" --regid="$gid" --clear-groups "$@"
fi

exec "$@"
