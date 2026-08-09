# Harness derivation — faculty-action — round 238

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When a computer action cannot be independently verified, tell me 'unknown' on the pendant and let me safely retry or cancel it with one deliberate gesture; retry only idempotent steps and verify again before reporting success."
- **useful because:** Prevents the most dangerous failure mode—claiming an email, browser change, or file operation succeeded when the executor lost contact—and gives the owner a safe recovery path without exposing credentials to the pendant.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the realtime model only to summarize the pending outcome; use deterministic policy and background models for idempotency classification and retry planning.
- **latency:** Pending status within 1 second of an ambiguous receipt; verification/retry within 5 seconds when the Mac/browser is online.
- **cost:** Low: usually one verifier call and no extra model call; occasional short realtime summary, under $0.01 per incident.
- **security:** The pendant receives only an opaque transaction ID, risk class, digest, and short summary—not page contents or secrets. Retry requires the existing physical approval latch; non-idempotent actions are cancel-only. Unknown remains unknown after deadline.
- **missing:** A recovery state machine that joins executor receipts to verify_operation_step and exposes retry/cancel choices; An idempotency declaration on each planned action; A compact pendant protocol for unknown/retry/cancel

### "When I am bench-testing the pendant, file a bug report automatically from its UART log, including the exact failing test, firmware revision, hardware identity, and a short redacted log excerpt, then leave the report in my AI-Pendant-Workspace."
- **useful because:** Turns a cryptic failed flash or audio test into a reproducible issue without making the owner copy logs by hand, while preserving a durable paper trail for regressions in the real device.
- **path:** pendant → mac-terminal → mac-planner → relay → dashboard
- **model tier:** Use deterministic parsing for test names, timestamps, revisions, and counters; use a cheaper background model only to summarize the already-redacted excerpt.
- **latency:** Create the local draft within 10 seconds after the UART session closes; never block the live voice path.
- **cost:** Usually near-zero API cost; dominated by local UART capture and optional summary generation under $0.02 per failure.
- **security:** Bench USB is explicitly a test/flash transport, not a product mode. Redact tokens, credentials, audio payloads, and secret.conf values before persistence; require confirmation before uploading logs off the Mac. Keep the raw log local and store only a bounded excerpt in the report.
- **missing:** A bounded read-only UART/serial capture on mac-terminal (the current action manifest has no serial reader); A redaction/parser for Zephyr and bridge logs; A workspace issue-file writer with stable test and firmware identifiers

### "After every audio firmware or bridge test, give me a signed plain-language acceptance card: sample rate and frame size, measured codec CPU, alias rejection, mic-drop rate, tx-starved count, and whether silence-before-speech passed; keep the card with the test artifact."
- **useful because:** Makes audio quality a fact the owner can trust rather than a configuration label, and catches regressions before a bad build reaches daily conversations.
- **path:** pendant → ESP32 audio bridge → mac-terminal → relay → dashboard
- **model tier:** No expensive model for measurements; deterministic scripts and on-device counters produce the card, with a cheap background model optionally formatting the explanation.
- **latency:** Generate within 30 seconds of a bench run; never run during the owner’s live conversation.
- **cost:** Negligible API cost; local measurement is the dominant resource and a 1–2 minute fixture run is acceptable.
- **security:** Store only test metadata and hashes by default; do not upload microphone fixtures or speech. Require explicit confirmation to share raw audio. USB remains bench-only.
- **missing:** A test orchestrator that runs scripts/audio-quality-probe.mjs and audio_path_probe against the connected bridge; A signed receipt format binding measurements to firmware revision, bridge identity, and fixture hash; A dashboard/history view for comparing acceptance cards across builds

### "Let me ask, “What did you use to decide that, and what private data crossed each device?” and receive a source-and-data-flow explanation for any answer or action, with sensitive values replaced by hashes or labels."
- **useful because:** The owner can trust the hive without wondering whether browser secrets, private mail, or microphone audio were silently sent through the relay or model. It turns privacy from a policy claim into something inspectable after each interaction.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic provenance collection and sensitivity labeling first; use a cheap background model only to turn the structured trace into a short explanation.
- **latency:** Do not slow ordinary replies; produce the explanation on demand within 3 seconds, or attach a compact provenance token to an action receipt immediately.
- **cost:** Low recurring cost; hashes, labels, and route metadata are local. Explanation generation is typically under $0.01.
- **security:** Never place secret values in the provenance record. The pendant receives only opaque source IDs, sensitivity classes, and hashes. Provenance itself may reveal private app names, so it needs owner-controlled retention and deletion.
- **missing:** A field-level sensitivity taint that follows data from browser/Mac capture through relay/model and back; A signed per-turn provenance envelope and retention policy; A dashboard query that joins provenance to action and verification receipts

### "When I say “make this private,” move the relevant browser or Mac work into a sealed local session: keep page contents and credentials on the Mac, send the relay only a redacted task/result, and automatically destroy the temporary session and its artifacts when I say “close it.”"
- **useful because:** The owner can use the assistant for taxes, health portals, work documents, and account settings without choosing between convenience and sending sensitive page contents through the hive.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → mac-terminal → dashboard
- **model tier:** Use deterministic local routing and redaction for the boundary; use the realtime model only for the owner’s short command and a redacted result. Local Mac models or rules should handle page interpretation whenever possible.
- **latency:** Enter sealed mode in under 2 seconds; ordinary local actions should remain under 5 seconds. Destruction should return a receipt within 3 seconds.
- **cost:** Low to moderate: primarily local compute; only short redacted summaries reach the expensive tier.
- **security:** Credentials and raw page contents must never enter relay logs, model prompts, pendant storage, or crash reports. Require explicit confirmation before leaving sealed mode, keep an append-only deletion receipt without content, and fail closed if redaction or local routing is unavailable.
- **missing:** A Mac-local sealed-session boundary with an explicit allowlist of apps, files, and browser origins; A streaming redaction/taint layer before any relay or model call; Atomic cleanup and a verifiable deletion receipt for temporary artifacts; A pendant status pattern that distinguishes sealed, ordinary, and failed-closed modes


## Changes it proposed to its own stack

### `hardware` — Add a secure element to the product pendant and make it the sole signer for physical approvals, device identity, offline queue manifests, and outcome acknowledgements. Keep private keys non-exportable, use monotonic counters and anti-rollback slots, and bind signatures to the relay transaction digest and device firmware version.
- **owner gets:** A stolen or cloned pendant could not approve purchases, messages, or other sensitive actions by replaying copied tokens. The owner gets physical consent that remains meaningful even after long offline periods and firmware updates.
- effort: High: select and procure a low-power secure element, wire I2C/SPI, integrate key provisioning and attestation into nRF9160 firmware, update relay verification and recovery tooling, and design a manufacturing/recovery ceremony.  ·  risk: Provisioning loss could brick approval on a device; provide a factory recovery path with explicit owner re-enrollment and never silently fall back to software keys. Firmware bugs could reject legitimate actions, so support a signed compatibility window and a read-only diagnostic mode.
- cost: Roughly $1–$4 per unit plus provisioning fixtures; negligible steady-state power, with tens of milliseconds per signature.  ·  latency: Adds approximately 20–100 ms to an approval envelope, acceptable for deliberate confirmation.
- security: Substantially improves anti-cloning and replay resistance. It does not protect a compromised relay from requesting a dangerous action, so keep the human-readable summary, expiry, digest, and independent verification requirements.
- depends on: physical_transaction_approval_latch; tactile_action_outcome_beacon; A product pendant revision rather than the current nRF9160 development kit; A documented key provisioning and recovery policy


## What it asked for

### `t30-ln21` (tool) — mac_bench_diagnostic
- why: The owner explicitly wants the pendant to file its own UART bug reports, and the connected nRF9160/ESP32 are real bench hardware. I need bounded read-only serial capture and correlation, not an unrestricted shell string.

```json
{
  "type": "object",
  "properties": {
    "operation": {
      "type": "string",
      "enum": [
        "list_serial_devices",
        "capture_uart",
        "read_jlink_identity"
      ]
    },
    "device": {
      "type": "string",
      "enum": [
        "nrf9160_pendant",
        "esp32_audio_bridge",
        "all"
      ]
    },
    "duration_ms": {
      "type": "integer",
      "minimum": 100,
      "maximum": 30000
    },
    "max_bytes": {
      "type": "integer",
      "minimum": 256,
      "maximum": 262144
    },
    "redact": {
      "type": "boolean",
      "default": true
    }
  },
  "required": [
    "operation"
  ]
}
```

