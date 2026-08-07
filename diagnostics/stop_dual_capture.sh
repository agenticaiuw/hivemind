#!/usr/bin/env bash
set -euo pipefail
OUT="$(cd "$(dirname "$0")" && pwd)"
if [[ -f "${OUT}/dual_capture.pid" ]]; then
	kill "$(cat "${OUT}/dual_capture.pid")" 2>/dev/null || true
	rm -f "${OUT}/dual_capture.pid"
fi
if [[ -e "${OUT}/dual-capture-latest" ]]; then
	for pf in "${OUT}/dual-capture-latest"/{nrf,esp,super}.pid; do
		[[ -f "$pf" ]] || continue
		kill "$(cat "$pf")" 2>/dev/null || true
		rm -f "$pf"
	done
fi
echo "dual capture stopped"
