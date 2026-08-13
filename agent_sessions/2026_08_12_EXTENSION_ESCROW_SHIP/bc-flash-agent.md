# bc-flash — board-controller routing, app rebuild, flash

Resumed run. The predecessor was killed by a UI stop mid-flight, not by an
error, so this log starts by inspecting what it left behind rather than
rebuilding it.

## Claimed files
- firmware/nrf9160/scripts/flash-board-controller.sh
- firmware/nrf9160/boards/nrf9160dk_nrf52840.overlay
- firmware/nrf9160/src/pendant_status.c
- build dirs: build-bc52840 (board controller), build-app-current (app)

NOT touched: firmware/nrf9160/selftest/ (hw-selftest's live work),
firmware/esp32-airpods-bridge/src/main.cpp (another agent's in-flight
sink-selection change — left uncommitted for its owner).

## Inherited from the killed run, verified rather than trusted
- `scripts/flash-board-controller.sh` — the recipe was already correct. The
  insight worth keeping: there is no separate "board controller sample".
  The board controller IS `boards/nordic/nrf9160dk/board.c`, which Zephyr
  links into ANY app built for `nrf9160dk/nrf52840`, and the routing comes
  entirely from devicetree. So the image is hello_world + our overlay.
- `build-bc52840/` — already built and correct.
- `build-rgbcal/` + modified `src/pendant_status.c` — per-channel RGB gain,
  already complete and compiling.

One stale artefact had to be cleaned up: a `sniff.py` reader (PID 15591)
left holding VCOM0 from the killed run. It was actively corrupting console
captures — the same read came back as shredded text with it alive
("tus LEDdy:=P0cATTED") and perfectly clean once killed. Worth remembering
that a killed agent can leave a process on a serial port.

## 1. Board controller: verification before flashing

The script's own `--verify` passes, but it parses the generated devicetree
with an awk one-liner that takes the first `status` line after a label —
which would also match a status belonging to a *nested* node. Re-checked
independently with a brace-matching parse of
`build-bc52840/hello_world/zephyr/zephyr.dts`, printing every routing node
rather than only the five expected to be off:

| node | status | control gpio |
| --- | --- | --- |
| vcom0_pins_routing | **okay** | &gpio1 14 |
| vcom2_pins_routing | disabled | &gpio1 12 |
| led1_pin_routing | okay | &gpio1 5 |
| led2_pin_routing | disabled | &gpio1 7 |
| led3_pin_routing | disabled | &gpio1 1 |
| led4_pin_routing | disabled | &gpio1 3 |
| button1_pin_routing | okay | &gpio0 6 |
| button2_pin_routing | disabled | &gpio0 26 |

All five required routings are genuinely disabled, and `vcom0` — the debug
console — is deliberately still ENABLED.

Cross-checked the pin claims against the Zephyr board documentation's own
default-routing table rather than against our overlay's comments, since a
comment cannot be evidence for itself. The table agrees exactly: VCOM2 =
P0.01/P0.00/P0.15/P0.14, LED2 = P0.03, LED3 = P0.04, LED4 = P0.05,
Button 2 = P0.07. So disabling these five frees P0.00 (UART TX to the
ESP32), P0.05 (UART RX), and P0.03/P0.04/P0.07 (the RGB legs).

### Is it the right image for THIS board?
- `model = "Nordic nRF9160 DK NRF52840"`, `compatible = "nordic,nrf9160-dk-nrf52840"`
- `CONFIG_BOARD_TARGET="nrf9160dk@0.14.0/nrf52840"`, `CONFIG_SOC="nrf52840"`
- Revision-specific check: on v0.7.0 `vcom2_pins_routing` needs TWO control
  pins driven (P1.12 *and* P0.12); on v0.14.0 it is P1.12 alone. The
  generated DT shows the single-pin form, i.e. the image really is built
  for the 0.14.0 board and not silently defaulted.

### Could this brick the debug link?
No — and the premise in the brief is worth correcting for the record.
**The nRF52840 is the board controller, not the debugger.** The debugger is
a separate SEGGER J-Link OB interface MCU; the Zephyr board docs describe
the board controller as routing nRF9160 pins *to* "the VCOMx of the
interface MCU", i.e. a distinct chip. SW10 mechanically muxes the J-Link's
SWD lines between the two targets, which is itself proof the probe is a
third device. Also checked:
- `CONFIG_NRF_APPROTECT_LOCK` is **not set** — the image cannot lock the
  chip out of debug.
- VCOM0 routing stays enabled, so the console survives.
- Worst case (a bad image) leaves the switches undriven, which costs the
  routing and nothing else; SW10 + reflash always recovers.

### NOT FLASHED — stood down on the coordinator's call
The image is verified and safe, but it was deliberately not programmed. The
five pins it frees are P0.00/P0.05 (ESP32 UART) and P0.03/P0.04/P0.07 (RGB
LED), and the owner has wired **none** of them — he is out of jumper wires
and resistors, so both the UART jumpers and the RGB LED are off the bench.
Flashing would have changed nothing observable while costing the owner a
manual SW10 flip, so the request for that flip was withdrawn.

This is the right call and worth stating as a rule: a verified image is not
the same as a needed flash. The blocker was never software.

Everything needed to finish it later now lives in the script's own header —
when it becomes necessary, the exact SW10 nRF52 -> flash -> nRF91 procedure,
the safety analysis, and the two symptoms that mean you skipped it. Nobody
has to re-derive any of it. `--help` prints the whole block (it now scans
the header rather than a hardcoded line range that would truncate as the
header grows).

## 2. RGB calibration — descoped, and correctly so

Owner has not wired the RGB LED (out of resistors and jumper wires) and it
is off the bench, so tuning it would be tuning something invisible. The
work was already in a finished state, so it was kept and compiled, not
extended:
- Per-channel ceilings replace the single `RGB_DUTY_CAP`:
  `RGB_DUTY_CEIL_RED 64`, `RGB_DUTY_CEIL_GREEN 224`, `RGB_DUTY_CEIL_BLUE 224`.
  Rationale documented in-file: red is GaAsP (~2.0 V Vf), green/blue are
  InGaN (3.0-3.2 V) on a 3.0 V rail, so equal duty makes the part a red LED
  with two decorative legs and "amber" stops reading as amber.
- Pads moved to high drive (H0H1) for the same headroom reason.
- Retuning order documented (resistor first, then ceilings) so the next
  person changes the knob that actually matters.

**Harmless with nothing attached — verified on hardware, not by reading.**
Boot log shows `Status LED ready: R=P0.03 G=P0.04 B=P0.07 (common-cathode)`
then `STATUS mic MUTED`: the state machine runs and drives three
unconnected pads. No fault, no hang.

A `status_ready` guard was also added, and it is not cosmetic: `main.c` now
calls `pendant_status_set(PENDANT_STATUS_FAILED)` from `show_error()`, and
`pendant_status_init()` moved above the first fatal path. Without the guard
a pre-init failure would reschedule an uninitialised work item and turn a
reportable boot failure into a kernel assert — losing the exact signal the
module exists to deliver.

## 3. Application image on the current tree

Fresh dir `build-app-current`, built against the tree WITH the
accelerometer removed:

    west build -b nrf9160dk/nrf9160/ns -d build-app-current . \
        -- -DEXTRA_CONF_FILE=secrets.conf

| region | used | size | % |
| --- | --- | --- | --- |
| FLASH | 413,700 B | 576 KB | 70.14% |
| RAM | 204,932 B | 211,608 B | 96.85% |

Against the status-LED baseline (414,524 B / 204,940 B) the accel removal
gives back 824 B of flash and 8 B of RAM. RAM is still the tight one at
96.85% — 6,676 B free.

Flashed via nrfutil (programmed + verified + reset). Confirmed running by
live console capture, not by assumption:

    Mic power sense ready (P0.26): mic is MUTED (power cut)
    Audio sink: bluetooth
    Volume knob ready (P0.15/AIN2, ratiometric, ~20 Hz poll)
    Haptic: DRV2605L not answering (-5) — haptic actions degrade to LED patterns
    Status LED ready: R=P0.03 G=P0.04 B=P0.07 (common-cathode)
    STATUS mic MUTED
    E: Card error on CMD0 / fs mount error (-5)   [x5]
    microSD is required for Internet voice upload

There is no accelerometer line at all any more — that is the removal
working. The DRV2605L and microSD errors are pre-existing absent hardware
on this bench, not regressions.

### Serial capture gotcha, for whoever reads VCOM0 next
VCOM0 is `/dev/cu.usbmodem0009600365811` at 115200. Use `/dev/cu.*`, never
`/dev/tty.*` (the tty node blocks on carrier detect). And `stty -f PORT
115200` followed by a separate `cat` does NOT work on macOS: closing the
stty handle resets the line to 9600 and you get binary garbage. The fd must
be opened first and stty applied while it is held — which is what
`sniff.py` does.

## Log
- Verified board-controller routings independently; confirmed board identity
  and revision; confirmed the flash cannot cost the debug link.
- Killed the stale VCOM0 reader left by the interrupted run.
- Built and flashed build-app-current; captured clean boot evidence.
- Pointed `flash-board-controller.sh`'s APP_BUILD default at
  `build-app-current` (it still said `build-rgbcal`, which predates the
  accel removal and would have put the board out of sync with the repo).
- Coordinated the J-Link with hw-selftest so the two of us never program at
  once, then released the probe and VCOM0 to it once the BC flash was
  cancelled (verified released: no nrfutil/JLink/west/sniff.py alive).
- Wrote the "when do I need this" header into the script so the cancelled
  flash is a documented waiting task, not lost work.

## Not committed here, on purpose
- `build-bc52840/`, `build-app-current/` — build output, already covered by
  `firmware/nrf9160/.gitignore` (`/build*/`).
- `firmware/esp32-airpods-bridge/src/main.cpp` — another agent's in-flight
  change to Bluetooth sink-selection policy. Unrelated to this work and not
  mine to land.
- `firmware/nrf9160/selftest/` — hw-selftest's live bench app, still running.
