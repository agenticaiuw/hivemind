# Harness derivation — mac-terminal — round 242

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/USB diagnostics** — mac_read_diagnostics and mac_usb_serial_diagnostics remain unresolved against the live inventory; no serial/USB capability is published. The live devices list shows only Safari, home-macbook-bridge, and an offline mobile device, so chip attachment cannot be inferred from HTTP discovery.
  - evidence: list_capabilities then discover devices; direct calls returned resolver verdicts with nearest GET /health/action:get_mac_status and no serial, usb, tty, or baud inventory.

## Capabilities it proposed

### ""Check the pendant bench before I rely on it." Read both chips over USB, tell me whether audio, button, storage, and bridge links are healthy, and keep a timestamped report I can compare after a firmware change."
- **useful because:** The hardware is physically present today but there is no trustworthy one-command answer about whether a failure is the nRF9160, ESP32 bridge, cable, or firmware. It turns an expensive guess into a concrete go/no-go before the owner wears it.
- **path:** mac-planner → relay-realtime → unified → faculty-perception
- **model tier:** background
- **latency:** 10-20 seconds for a bounded 5-second dual-UART capture; no realtime model needed.
- **cost:** Low: one short background inference over parsed UART counters; shell capture and parsing dominate, not tokens.
- **security:** USB logs remain on the Mac by default; send only parsed counters, firmware versions, timestamps, and pass/fail to the relay. Never upload raw audio or arbitrary UART payloads without an explicit debug request.
- **missing:** A production bench-health action that invokes diagnostics/dual_chip_autocapture.sh or equivalent bounded read-only serial capture and parses both protocols; A stable health schema for nRF9160, ESP32, cable enumeration, and capture age; A relay route to store and compare successive health reports

### ""Find where I left that thing." Search my open Safari tabs, recent Mac files, pending Mac jobs, and the relay's saved browser findings, then give me the shortest answer with the exact source and a one-click way to reopen it."
- **useful because:** Today each surface knows only its own slice. The owner can lose an item between a logged-in browser page, a downloaded file, and a queued Mac job; a cross-surface, provenance-first answer would recover it without repeating the search.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** background
- **latency:** Under 8 seconds; parallel reads first, cheap ranking second, realtime only to speak the answer.
- **cost:** Low to moderate: parallel metadata reads and a small synthesis; no page screenshots unless structured data fails.
- **security:** Search results can expose authenticated titles and paths. Keep page bodies local, return only the minimum matching metadata, attach source URLs/paths, and require the existing action mechanism before opening or moving anything.
- **missing:** A single fan-out search operation spanning browser tabs, local file metadata, jobs, and browser findings; A provenance-aware ranker that refuses unsupported matches and preserves source URLs/paths; A compact spoken result plus reopen action that can target either Safari or Finder

### ""Repair this failed task, but show me exactly what changed." Hand the failure from the Mac to the browser for documentation lookup when needed, let the Mac run a minimal diagnosis and reversible repair, and return a before/after proof to the pendant."
- **useful because:** A failed command currently collapses into a message with no exit code, no durable retry, and no proof that a repair worked. This would make the hive useful during real work rather than merely reporting that something broke.
- **path:** mac-planner → browser-extension → relay-realtime → pendant → faculty-action
- **model tier:** background for diagnosis and documentation; realtime only for the owner's live clarification.
- **latency:** 30-90 seconds for diagnosis and one repair attempt; stop after a bounded attempt and report honestly.
- **cost:** Moderate: shell execution dominates; browser lookup and one small synthesis are cheaper than a full computer-use loop.
- **security:** The owner permits maximum Mac access, so do not add a new approval gate. Instead, record the exact command, cwd, exit status, changed paths, rollback availability, and documentation URLs; never send environment secrets or raw build artifacts to the relay.
- **missing:** Structured shell receipts with exit code, signal, duration, cwd, and redacted environment fingerprint; A bounded retry/repair planner with explicit before/after checks and rollback metadata; A cross-surface handoff that lets browser documentation inform a Mac repair while keeping command output local

### ""Make the reply audible before I start relying on this pendant." Run a local acoustic self-test across the ESP32 bridge, pendant speaker path, and Mac audio route; detect clipping, silence, latency, or a wrong output device, then select the best codec/volume profile and prove it with a short loopback."
- **useful because:** A conversation that technically connects but cannot be heard is a silent failure. Today the owner must diagnose cables, output routing, codec settings, and volume by trial and error; this would turn first-use audio into a measurable pass/fail.
- **path:** pendant → mac-planner → relay-realtime → unified
- **model tier:** background for calibration and comparison; realtime only after the path passes.
- **latency:** 15 seconds maximum for a bounded tone-and-loopback test, then immediate spoken confirmation.
- **cost:** Low API cost; most work is local signal generation and measurement. Hardware may need a small calibration fixture or firmware loopback mode.
- **security:** Generate a synthetic test tone only; never open the Mac microphone. Keep measurements local and send only scalar latency, level, clipping, and selected-profile data to the relay.
- **missing:** A pendant/ESP32 acoustic loopback diagnostic mode with deterministic test tones and level counters; A Mac action that identifies and verifies the selected audio route without microphone capture; A profile store shared by the bridge and relay, with rollback to the previous known-good profile

### ""Update both chips, but do not leave me with a dead pendant." Flash a signed, matched firmware pair, capture boot and health evidence from both USB devices, run a voice-path smoke test, and automatically restore the last known-good pair if either side regresses."
- **useful because:** The owner can physically flash firmware today, but cannot get an end-to-end answer that the nRF9160 and ESP32 still agree after the update. A failed update currently becomes a manual hardware recovery exercise.
- **path:** mac-planner → pendant → relay-realtime → unified → faculty-action
- **model tier:** background; firmware flashing and health tests are deterministic, with realtime only to report the result.
- **latency:** 2-5 minutes, dominated by flashing and boot stabilization; never claim success before both chips pass.
- **cost:** Low model cost; USB flashing and boot capture dominate. Requires local storage for two firmware images and logs.
- **security:** Require signed or hash-pinned images, preserve the prior pair locally, and never send raw boot logs or firmware binaries to the relay. Recovery must be explicit and auditable even though the owner does not want approval gates for ordinary work.
- **missing:** A paired firmware manifest tying nRF9160 and ESP32 versions together; A transactional flasher with boot readiness checks and rollback; A post-flash audio/button smoke test that can run offline over USB

### ""Pair this freshly attached pendant with my Mac and relay." Perform a physical-presence challenge over USB, verify the nRF9160 and ESP32 identities as one device, bind that pair to the owner's relay identity, and tell me exactly which hardware is trusted before enabling voice actions."
- **useful because:** A cable can attach the wrong board, a stale firmware image, or a bridge belonging to another setup. Today there is no owner-facing ceremony that proves the two chips and the relay are the same pendant before use.
- **path:** pendant → mac-planner → relay-realtime → unified
- **model tier:** background deterministic protocol; no expensive model needed except to explain failures.
- **latency:** Under 30 seconds for challenge, identity exchange, and persistence.
- **cost:** Negligible inference cost; engineering work is a small authenticated protocol and durable pairing record.
- **security:** Use a one-time physical challenge and device-held private keys; expose only stable device IDs and attestation status to the relay. Do not rely on USB port names or unauthenticated serial text.
- **missing:** A device identity and attestation protocol spanning both chips; A relay pairing endpoint and durable revocation record; A local pairing UI/voice report that distinguishes nRF9160, ESP32, and cable mismatches


## What it asked for

_Nothing._
