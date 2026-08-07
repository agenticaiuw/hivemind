#!/usr/bin/env bash
# Simple dual UART capture for nRF9160 + ESP32. Press Ctrl-C on stop script to end.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/diagnostics"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN="${OUT}/dual-capture-${STAMP}"
mkdir -p "$RUN"

NRF_PORT="${NRF_UART_PORT:-}"
ESP_PORT="${ESP_UART_PORT:-}"
NRF_BAUD=115200
ESP_BAUD=115200

if [[ -z "$NRF_PORT" ]]; then
	shopt -s nullglob
	c=(/dev/cu.usbmodem*1)
	(( ${#c[@]} )) || c=(/dev/cu.usbmodem*)
	NRF_PORT="${c[0]:-}"
fi
if [[ -z "$ESP_PORT" ]]; then
	shopt -s nullglob
	c=(/dev/cu.usbserial*)
	ESP_PORT="${c[0]:-}"
fi

# Stop previous
if [[ -f "${OUT}/dual_capture.pid" ]]; then
	old="$(cat "${OUT}/dual_capture.pid")"
	if [[ -n "$old" ]]; then
		# kill tree: supervisor + children listed in old run
		kill "$old" 2>/dev/null || true
	fi
	rm -f "${OUT}/dual_capture.pid"
fi
# Best-effort: kill our labeled capture helpers by pid files in latest
if [[ -e "${OUT}/dual-capture-latest" ]]; then
	for pf in "${OUT}/dual-capture-latest"/{nrf,esp,super}.pid; do
		[[ -f "$pf" ]] || continue
		kill "$(cat "$pf")" 2>/dev/null || true
	done
fi

ln -sfn "dual-capture-${STAMP}" "${OUT}/dual-capture-latest"
ln -sfn "dual-capture-${STAMP}/nrf.log" "${OUT}/nrf-uart-latest.log"
ln -sfn "dual-capture-${STAMP}/esp.log" "${OUT}/esp-uart-latest.log"
: >"${OUT}/dual-capture-live.log"

{
	echo "=== dual capture ${STAMP} ==="
	echo "nrf_port=${NRF_PORT:-MISSING}"
	echo "esp_port=${ESP_PORT:-MISSING}"
	echo "run=${RUN}"
	echo "started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} | tee "${RUN}/meta.txt"

capture_uart() {
	local port="$1" baud="$2" label="$3" log="$4" raw="$5"
	if [[ -z "$port" || ! -e "$port" ]]; then
		echo "SKIP ${label}: no port" | tee -a "${RUN}/meta.txt"
		return 1
	fi
	# Keep port open while configuring baud (macOS)
	exec 3<>"$port"
	if ! stty "$baud" raw -echo -ixon -ixoff <&3; then
		echo "FAIL stty ${label} ${port}" | tee -a "${RUN}/meta.txt"
		exec 3<&-
		return 1
	fi
	{
		echo "=== ${label} start $(date -u +%Y-%m-%dT%H:%M:%SZ) port=${port} baud=${baud} ==="
	} | tee -a "$log" >>"${RUN}/meta.txt"

	# Background: read from FD 3 (inherited)
	(
		python3 -u - "$label" "$log" "$raw" "${OUT}/dual-capture-live.log" 3<&3 <<'PY'
import sys, os, datetime

label, log_path, raw_path, live_path = sys.argv[1:5]
# FD 3 is the serial port
ser = os.fdopen(3, "rb", buffering=0)
log = open(log_path, "a", buffering=1)
raw = open(raw_path, "ab", buffering=0)
live = open(live_path, "a", buffering=1)
buf = b""
try:
    while True:
        chunk = ser.read(256)
        if not chunk:
            # brief yield; some USB CDC returns empty when idle
            import time
            time.sleep(0.02)
            continue
        raw.write(chunk)
        raw.flush()
        buf += chunk
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            try:
                text = line.decode("utf-8", errors="replace").rstrip("\r")
            except Exception:
                text = repr(line)
            ts = datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%f"
            )[:-3] + "Z"
            row = f"{ts} [{label}] {text}\n"
            log.write(row)
            live.write(row)
            log.flush()
            live.flush()
except Exception as e:
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    msg = f"{ts} [{label}] CAPTURE_ERROR {e}\n"
    log.write(msg)
    live.write(msg)
PY
	) &
	echo $! >"${RUN}/${label}.pid"
	echo "${label} pid=$(cat "${RUN}/${label}.pid") port=${port}" | tee -a "${RUN}/meta.txt"
	# Do not close FD 3 in parent until after both captures started — use a new FD for second.
	return 0
}

# nRF on FD 3, ESP on FD 4 — run as separate subshells so each owns its FD
if [[ -n "${NRF_PORT}" && -e "${NRF_PORT}" ]]; then
	(
		exec 3<>"$NRF_PORT"
		stty "$NRF_BAUD" raw -echo -ixon -ixoff <&3
		echo "=== nrf start $(date -u +%Y-%m-%dT%H:%M:%SZ) port=${NRF_PORT} ===" | tee -a "${RUN}/nrf.log" >>"${RUN}/meta.txt"
		python3 -u - "nrf" "${RUN}/nrf.log" "${RUN}/nrf.raw" "${OUT}/dual-capture-live.log" 3<&3 <<'PY'
import sys, os, datetime, time
label, log_path, raw_path, live_path = sys.argv[1:5]
ser = os.fdopen(3, "rb", buffering=0)
log = open(log_path, "a", buffering=1)
raw = open(raw_path, "ab", buffering=0)
live = open(live_path, "a", buffering=1)
buf = b""
while True:
    chunk = ser.read(256)
    if not chunk:
        time.sleep(0.02)
        continue
    raw.write(chunk); raw.flush()
    buf += chunk
    while b"\n" in buf:
        line, buf = buf.split(b"\n", 1)
        text = line.decode("utf-8", errors="replace").rstrip("\r")
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        row = f"{ts} [{label}] {text}\n"
        log.write(row); live.write(row); log.flush(); live.flush()
PY
	) &
	echo $! >"${RUN}/nrf.pid"
	echo "nrf pid=$(cat "${RUN}/nrf.pid") port=${NRF_PORT}" | tee -a "${RUN}/meta.txt"
else
	echo "SKIP nrf: no port" | tee -a "${RUN}/meta.txt"
fi

if [[ -n "${ESP_PORT}" && -e "${ESP_PORT}" ]]; then
	(
		exec 3<>"$ESP_PORT"
		stty "$ESP_BAUD" raw -echo -ixon -ixoff <&3
		echo "=== esp start $(date -u +%Y-%m-%dT%H:%M:%SZ) port=${ESP_PORT} ===" | tee -a "${RUN}/esp.log" >>"${RUN}/meta.txt"
		python3 -u - "esp" "${RUN}/esp.log" "${RUN}/esp.raw" "${OUT}/dual-capture-live.log" 3<&3 <<'PY'
import sys, os, datetime, time
label, log_path, raw_path, live_path = sys.argv[1:5]
ser = os.fdopen(3, "rb", buffering=0)
log = open(log_path, "a", buffering=1)
raw = open(raw_path, "ab", buffering=0)
live = open(live_path, "a", buffering=1)
buf = b""
while True:
    chunk = ser.read(256)
    if not chunk:
        time.sleep(0.02)
        continue
    raw.write(chunk); raw.flush()
    buf += chunk
    while b"\n" in buf:
        line, buf = buf.split(b"\n", 1)
        text = line.decode("utf-8", errors="replace").rstrip("\r")
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        row = f"{ts} [{label}] {text}\n"
        log.write(row); live.write(row); log.flush(); live.flush()
PY
	) &
	echo $! >"${RUN}/esp.pid"
	echo "esp pid=$(cat "${RUN}/esp.pid") port=${ESP_PORT}" | tee -a "${RUN}/meta.txt"
else
	echo "SKIP esp: no port" | tee -a "${RUN}/meta.txt"
fi

# Supervisor waits on children
(
	echo $$ >"${RUN}/super.pid"
	# wait for nrf/esp children if present
	pids=()
	[[ -f "${RUN}/nrf.pid" ]] && pids+=("$(cat "${RUN}/nrf.pid")")
	[[ -f "${RUN}/esp.pid" ]] && pids+=("$(cat "${RUN}/esp.pid")")
	if (( ${#pids[@]} )); then
		wait "${pids[@]}" 2>/dev/null || true
	else
		sleep infinity
	fi
) &
echo $! >"${OUT}/dual_capture.pid"

sleep 0.5
echo "ARMED"
echo "  live:  tail -f ${OUT}/dual-capture-live.log"
echo "  nrf:   ${RUN}/nrf.log"
echo "  esp:   ${RUN}/esp.log"
echo "  stop:  ${OUT}/stop_dual_capture.sh"
[[ -f "${RUN}/nrf.pid" ]] && ps -p "$(cat "${RUN}/nrf.pid")" -o pid=,command= || echo "nrf dead"
[[ -f "${RUN}/esp.pid" ]] && ps -p "$(cat "${RUN}/esp.pid")" -o pid=,command= || echo "esp dead"
