#!/bin/sh
# Serve the explorer. file:// can't fetch the data files, so it needs a server.
cd "$(dirname "$0")" || exit 1
PORT="${1:-8777}"
echo "SaveSage Card Explorer  ->  http://localhost:$PORT/ui/"
echo "Ctrl-C to stop."
exec python3 -m http.server "$PORT" --bind 127.0.0.1
