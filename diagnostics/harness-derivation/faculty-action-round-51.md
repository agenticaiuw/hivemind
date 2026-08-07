# Harness derivation — faculty-action — round 51

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-path** — The currently documented pendant audio path is I2S capture at 15,625 Hz with Opus uplink labeled 16 kHz/16 kbps; the bridge is an ESP32 classic and network is LTE-M half-duplex in practice. Therefore a true 24 kHz path cannot be claimed from relay/model changes alone.
  - evidence: discover:hardware audio/network/bridge summaries in this round

## Capabilities it proposed

### "“Use the best voice quality available.” The system should negotiate a true 24 kHz superwideband path end to end, fall back safely when LTE or a peer cannot sustain it, and tell me which mode is actually active."
- **useful because:** The owner currently has a 15,625 Hz microphone feeding a nominal 16 kHz Opus uplink; a model may decide that high-quality speech is desirable but cannot make every hand in the chain agree. This capability makes the decision executable: the pendant, bridge, relay, and Mac playback each advertise measured capabilities, the relay selects a mode, and the pendant gets a short spoken/LED indication of the real mode rather than a promise. It also produces a per-turn quality receipt so regressions are diagnosable.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime only for the live codec/transport negotiation and one-sentence user feedback; no LLM is needed in the audio loop. A cheaper background worker can aggregate quality receipts and detect regressions.
- **latency:** Negotiation <=150 ms before capture, no added steady-state conversational latency beyond one Opus frame; fallback within 2 seconds of sustained loss/jitter. Dashboard receipt can lag by minutes.
- **cost:** Negligible model cost in the hot path; roughly $0.001–$0.01 per session for relay compute/storage depending on retention and telemetry volume. The dominant cost is LTE airtime and storing dual-mode test recordings, not inference.
- **security:** Raw audio remains sensitive: do not upload diagnostic PCM by default. Send compact telemetry (mode, packet loss, jitter, sample counts, codec settings), encrypt receipts, and retain audio only under the existing policy. Changing mode is non-destructive and needs no confirmation; exporting recordings or sharing receipts requires confirmation.
- **missing:** A firmware capture/codec implementation that genuinely produces 24 kHz samples (the current hardware contract reports 15,625 Hz capture), with resampler quality and CPU/RAM measurements; A versioned audio-capability handshake shared by pendant, ESP32 bridge, relay, and Mac playback, including an explicit reason-coded fallback; A relay jitter buffer and sequence/timestamp validation that can distinguish 24 kHz content from mislabeled 16 kHz frames; A Mac-side loopback/measurement harness and golden fixtures (sweep, speech, packet-loss simulation) to verify sample rate, intelligibility, and latency before claiming success; A compact pendant status indication and durable quality receipt linked to the conversation/job id

### "“Do it, and prove it worked.” For any reversible cross-device action, verify the resulting state on the surface that owns it, and tell me if execution succeeded, is merely queued, or could not be verified."
- **useful because:** Today an action agent can queue a Mac or browser command and produce a receipt, but a queued receipt is not proof that the world changed. This closes the gap between judgement and action: after creating a reminder, the Mac reads it back; after a browser form mutation, the browser re-reads the authoritative page; after a pendant setting change, the relay receives a device acknowledgement. The owner gets one concise result and no false claims of completion.
- **path:** faculty-action → mac-bridge → browser-extension → relay-realtime → faculty-perception → dashboard
- **model tier:** No expensive model for deterministic verification. faculty-judgement supplies the typed expected postcondition; action executes it; faculty-perception compares observed state. Realtime is used only to speak the result if the owner is present; background retries use a cheaper worker.
- **latency:** Immediate local verification within 1 second; browser/server confirmation within 5 seconds, with durable polling up to 2 minutes after disconnect. If the postcondition is not observable, report ‘unverified’ rather than retrying blindly.
- **cost:** Near-zero inference cost for typed predicates; roughly $0.001 per browser verification and minimal Mac/relay compute. Storage is a small before/after evidence record, not a copy of page contents or audio.
- **security:** Verification reads private state and must inherit the action’s tab/session permissions. Redact secrets and page bodies from receipts, retain only field hashes plus minimal evidence, and never turn a failed verification into an automatic repeat for side-effectful operations. Destructive actions remain confirmation-gated.
- **missing:** A shared typed postcondition schema (entity, owner surface, predicate, timeout, freshness) emitted by faculty-judgement; Per-surface verify adapters: Mac read-back, browser authoritative re-read, and pendant/relay device ACK with monotonic sequence numbers; A state-machine result distinct from success: queued, applied, verified, rejected, timed out, and unknown-after-disconnect; Evidence-safe receipt storage and dashboard rendering that shows expected versus observed without leaking private values; Idempotency/lease integration so reconnect verification cannot replay the original mutation

### "“Use my saved information to complete this, but never show or send my private values through the AI.” The system should let the browser or Mac fill secrets locally, have the pendant show only a redacted summary, and require my physical approval immediately before submission."
- **useful because:** The owner can ask for a form or account task, but today the model either needs the values in its context or cannot reliably coordinate private autofill with a safe final approval. This would let the AI prepare a transaction without learning passwords, payment details, recovery codes, or other secrets. The browser session or Mac Keychain remains the only component that handles the plaintext; the pendant and relay carry field labels, redacted previews, and a signed approval instead.
- **path:** faculty-judgement → faculty-action → browser-extension → mac-bridge → relay-realtime → pendant → dashboard
- **model tier:** Use a cheaper planning model to map requested fields to typed intents. No model should receive secret values. Realtime is used only to explain the redacted preview and collect the final physical approval.
- **latency:** Prepare the redacted transaction preview within 3 seconds; local secret filling under 1 second; approval must expire after 60 seconds and submission acknowledgement should arrive within 5 seconds. Never continue submission after a disconnect or stale preview.
- **cost:** Near-zero inference cost after the initial field-intent plan. Main engineering cost is browser/Mac integration and security review; operational cost is a few encrypted metadata bytes per transaction, with no secret storage.
- **security:** Secrets must never enter prompts, relay logs, D1, R2, screenshots, or dashboard history. Use OS Keychain/browser autofill handles or opaque local references, scoped to origin and field name. Bind approval to origin, account, field names, redacted value fingerprints, and a short expiry; reject if any changes. Require confirmation for submission, purchases, messages, or other irreversible effects.
- **missing:** A local secret-provider adapter for Safari/Chrome autofill and macOS Keychain that returns opaque handles rather than values; A redacted transaction manifest with origin binding, field metadata, value fingerprints, and an immutable preview hash; A pendant approval protocol that displays safe labels and commits only the exact previewed manifest; Browser and Mac submit gates that refuse altered DOM, navigation, origin, or stale approvals; End-to-end tests proving plaintext secrets never appear in model context, relay telemetry, screenshots, or receipts


## What it asked for

### `t23-jjid` (tool) — audio_path_probe
- why: I need to execute the owner’s explicit 24 kHz end-to-end audio goal rather than merely propose it. Existing Mac/browser action tools cannot measure I2S sample clocks, Opus frame metadata, LTE jitter, or round-trip playback, and success cannot be claimed from configuration labels.

```json
{
  "type": "object",
  "properties": {
    "mode": {
      "type": "string",
      "enum": [
        "capabilities",
        "loopback",
        "golden_fixture",
        "live_measurement"
      ]
    },
    "duration_ms": {
      "type": "integer",
      "minimum": 1000,
      "maximum": 60000
    },
    "inject_packet_loss_pct": {
      "type": "number",
      "minimum": 0,
      "maximum": 50
    },
    "fixture": {
      "type": "string",
      "enum": [
        "speech",
        "sweep",
        "silence",
        "none"
      ]
    },
    "persist_receipt": {
      "type": "boolean"
    }
  },
  "required": [
    "mode"
  ]
}
```

