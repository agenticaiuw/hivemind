#!/usr/bin/env bash
# Dual-chip UART auto-capture: nRF9160 pendant + ESP32 A2DP bridge.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/diagnostics"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${OUT}/dual-capture-${STAMP}"
PID_FILE="${OUT}/dual_capture.pid"
META="${RUN_DIR}/meta.txt"

NRF_BAUD="${NRF_UART_BAUD:-115200}"
ESP_BAUD="${ESP_UART_BAUD:-115200}"
NRF_PORT="${NRF_UART_PORT:-}"
ESP_PORT="${ESP_UART_PORT:-}"

mkdir -p "$RUN_DIR"

pick_nrf_port() {
	if [[ -n "$NRF_PORT" ]]; then
		echo "$NRF_PORT"
		return
	fi
	shopt -s nullglob
	local c=(/dev/cu.usbmodem*1)
	if (( ${#c[@]} == 0 )); then
		c=(/dev/cu.usbmodem*)
	fi
	if (( ${#c[@]} == 0 )); then
		echo ""
		return
	fi
	echo "${c[0]}"
}

pick_esp_port() {
	if [[ -n "$ESP_PORT" ]]; then
		echo "$ESP_PORT"
		return
	fi
	shopt -s nullglob
	for p in /dev/cu.usbserial*; do
		echo "$p"
		return
	done
	echo ""
}

timestamp_lines() {
	local label="$1"
	python3 -u -c '
import sys, datetime
label = sys.argv[1]
for line in sys.stdin:
    line = line.rstrip("\n\r")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    print(f"{ts} [{label}] {line}", flush=True)
' "$label"
}

stop_existing() {
	if [[ -f "$PID_FILE" ]]; then
		local old
		old="$(cat "$PID_FILE" 2>/dev/null || true)"
		if [[ -n "$old" ]]; then
			# Kill whole process group if we started with setsid
			kill -- "-$old" 2>/dev/null || kill "$old" 2>/dev/null || true
			sleep 0.2
			kill -9 -- "-$old" 2>/dev/null || kill -9 "$old" 2>/dev/null || true
		fi
		rm -f "$PID_FILE"
	fi
	if [[ -L "${OUT}/dual-capture-latest" || -d "${OUT}/dual-capture-latest" ]]; then
		local d
		d="$(readlink "${OUT}/dual-capture-latest" 2>/dev/null || true)"
		if [[ -n "$d" && -d "${OUT}/$d" ]]; then
			for pf in "${OUT}/${d}"/*.pid; do
				[[ -f "$pf" ]] || continue
				p="$(cat "$pf" 2>/dev/null || true)"
				[[ -n "$p" ]] && kill "$p" 2>/dev/null || true
			done
		fi
	fi
}

capture_one() {
	local port="$1"
	local baud="$2"
	local label="$3"
	local log="$4"
	local raw="$5"

	if [[ -z "$port" || ! -e "$port" ]]; then
		echo "WARN: ${label} port missing (${port:-unset}); skip" | tee -a "$META"
		return 1
	fi

	# Open port on a fixed FD, set baud while held open (macOS requirement).
	exec 9<>"$port"
	if ! stty "$baud" raw -echo -ixon -ixoff <&9 2>/dev/null; then
		echo "WARN: could not configure ${port} @ ${baud}" | tee -a "$META"
		exec 9<&-
		return 1
	fi

	{
		echo "=== ${label} capture start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
		echo "port=${port} baud=${baud}"
	} | tee -a "$log" >>"$META"

	# Duplicate FD for background cat so we can close 9 in parent after spawn setup.
	# Use /dev/fd on macOS.
	(
		# shellcheck disable=SC2094
		cat <&9 | tee -a "$raw" | timestamp_lines "$label" | tee -a "$log" >>"${OUT}/dual-capture-live.log"
	) &
	local cpid=$!
	echo "$cpid" >"${RUN_DIR}/${label}.pid"
	echo "${label} pid=${cpid} port=${port}" | tee -a "$META"
	# Keep FD open in parent by not closing — child inherited it.
	# Actually after fork, parent still has 9; leave open until process exits.
	# Move to high unused by reopening next port on 8 for esp.
	return 0
}

if [[ "${1:-}" == "stop" ]]; then
	stop_existing
	echo "dual capture stopped"
	exit 0
fi

stop_existing

NRF_PORT="$(pick_nrf_port)"
ESP_PORT="$(pick_esp_port)"

{
	echo "=== dual-chip auto-capture ${STAMP} ==="
	echo "run_dir=${RUN_DIR}"
	echo "nrf_port=${NRF_PORT:-none}"
	echo "esp_port=${ESP_PORT:-none}"
	echo "started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
	echo "Do the full pendant routine (record → stop → wait for solid/ready LED → press play)."
	echo "Watch: LAT lines, I2S mic, upload, Agent reply, bridge/connected, a2dp"
} | tee "$META"

ln -sfn "dual-capture-${STAMP}" "${OUT}/dual-capture-latest"
ln -sfn "dual-capture-${STAMP}/nrf.log" "${OUT}/nrf-uart-latest.log"
ln -sfn "dual-capture-${STAMP}/esp.log" "${OUT}/esp-uart-latest.log"
: >"${OUT}/dual-capture-live.log"

# Run supervisor in background with its own process group
setsid bash -c "
set -euo pipefail
RUN_DIR='$RUN_DIR'
OUT='$OUT'
META='$META'
NRF_PORT='$NRF_PORT'
ESP_PORT='$ESP_PORT'
NRF_BAUD='$NRF_BAUD'
ESP_BAUD='$ESP_BAUD'

timestamp_lines() {
  local label=\"\$1\"
  python3 -u -c '
import sys, datetime
label = sys.argv[1]
for line in sys.stdin:
    line = line.rstrip(\"\\n\\r\")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime(\"%Y-%m-%dT%H:%M:%S.%f\")[:-3] + \"Z\"
    print(f\"{ts} [{label}] {line}\", flush=True)
' \"\$label\"
}

start_cap() {
  local port=\"\$1\" baud=\"\$2\" label=\"\$3\" log=\"\$4\" raw=\"\$5\" fd=\"\$6\"
  if [[ -z \"\$port\" || ! -e \"\$port\" ]]; then
    echo \"WARN: \${label} port missing (\${port:-unset})\" | tee -a \"\$META\"
    return 1
  fi
  eval \"exec \${fd}<>\\\"\\\$port\\\"\"
  if ! eval \"stty \\\$baud raw -echo -ixon -ixoff <&\\\$fd\" 2>/dev/null; then
    echo \"WARN: stty failed on \$port\" | tee -a \"\$META\"
    return 1
  fi
  {
    echo \"=== \${label} capture start \$(date -u +%Y-%m-%dT%H:%M:%SZ) ===\"
    echo \"port=\${port} baud=\${baud}\"
  } | tee -a \"\$log\" >>\"\$META\"
  eval \"cat <&\\\$fd\" | tee -a \"\$raw\" | timestamp_lines \"\$label\" | tee -a \"\$log\" >>\"\${OUT}/dual-capture-live.log\" &
  echo \$! >\"\${RUN_DIR}/\${label}.pid\"
  echo \"\${label} pid=\$(cat \${RUN_DIR}/\${label}.pid) port=\${port}\" | tee -a \"\$META\"
}

start_cap \"\$NRF_PORT\" \"\$NRF_BAUD\" nrf \"\${RUN_DIR}/nrf.log\" \"\${RUN_DIR}/nrf.raw\" 9 || true
start_cap \"\$ESP_PORT\" \"\$ESP_BAUD\" esp \"\${RUN_DIR}/esp.log\" \"\${RUN_DIR}/esp.raw\" 8 || true
echo ARMED | tee -a \"\$META\"
wait
" >/dev/null 2>>"${RUN_DIR}/supervisor.err" &

SUPER_PID=$!
echo "$SUPER_PID" >"$PID_FILE"
echo "supervisor pid=${SUPER_PID} pidfile=${PID_FILE}"
echo "Logs:"
echo "  ${RUN_DIR}/nrf.log"
echo "  ${RUN_DIR}/esp.log"
echo "  ${OUT}/dual-capture-live.log"
echo "Stop: $0 stop"
sleep 0.8
if [[ -f "${RUN_DIR}/nrf.pid" ]]; then
	echo "nrf capture ok pid=$(cat "${RUN_DIR}/nrf.pid")"
else
	echo "WARN: nrf capture may have failed — see ${RUN_DIR}/supervisor.err ${META}"
	cat "${RUN_DIR}/supervisor.err" 2>/dev/null || true
fi
if [[ -f "${RUN_DIR}/esp.pid" ]]; then
	echo "esp capture ok pid=$(cat "${RUN_DIR}/esp.pid")"
else
	echo "WARN: esp capture may have failed"
fi
