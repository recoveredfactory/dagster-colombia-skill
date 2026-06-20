#!/usr/bin/env bash
# Serve the deck locally. Markdown can't be fetched from file://, so we need HTTP.
# Usage: ./serve.sh [port]   (default 8000)
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-8000}"
echo "Deck:    http://localhost:${PORT}/"
echo "Spanish: http://localhost:${PORT}/?lang=es"
echo "PDF:     http://localhost:${PORT}/?print-pdf"
echo "(Ctrl-C to stop)"
exec python3 -m http.server "${PORT}"
