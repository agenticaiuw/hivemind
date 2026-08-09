# Harness derivation — mac-terminal — round 197

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “handle this,” let me walk away: have the pendant capture the request, the Mac and my authenticated browser do the work, and tell me on the pendant exactly what happened, what changed, and what still needs me."
- **useful because:** This is the single most useful hive capability: the owner gets an accountable personal operator rather than a chat response. It combines the pendant's always-present intent, the Mac's local files/apps, the browser's private sessions, and the relay's durable coordination; it remains useful when the owner is no longer looking at the screen.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard-ux
- **model tier:** Use realtime only to transcribe/clarify the short spoken request; use a cheaper background planner for multi-step execution and summarization, with no expensive model on polling or receipt formatting.
- **latency:** Acknowledge on the pendant in under 1 second; dispatch in under 3 seconds; long work may run asynchronously. Speak a checkpoint at each meaningful phase and a final result when complete.
- **cost:** Roughly one realtime turn for capture plus 1–2 background planning/summarization calls; dominant cost is model context for multi-step browser/Mac work, not transport.
- **security:** Browser pages, local files, and command output may contain secrets. Keep raw evidence on the Mac/browser, send the relay only a redacted result capsule and provenance IDs; never claim success without a completed receipt. Any irreversible action remains the owner's existing deliberate maximum-access policy, but the spoken result must name exactly what ran.
- **missing:** A durable cross-surface work envelope joining pendant turn ID, relay job ID, Mac job ID, browser command IDs, and ledger/receipt IDs; A result-capsule route that streams redacted checkpoints and provenance to the pendant; Boot recovery that reconciles interrupted Mac jobs and resumes only explicitly replay-safe steps; A real USB serial health/bench adapter so the currently attached pendant can be the intent/status endpoint today

### "Run a two-minute pendant bench check and tell me whether the worn device, USB link, ESP32 audio bridge, speaker path, and button/status path are healthy—with measured latency and the first failing component, not just “online.”"
- **useful because:** The chips are physically attached now but unregistered with the relay. This gives the owner a concrete way to validate the wearable before trusting it away from the Mac, and turns vague silence into a component-level diagnosis. It is a genuinely cross-node capability: the pendant generates known button/audio frames, the ESP32 returns loopback counters, the Mac timestamps USB transport, and the relay presents the result.
- **path:** pendant → mac-terminal → relay → dashboard-ux
- **model tier:** No realtime model for the test itself; deterministic firmware and Mac measurements, followed by a cheap background formatter. Escalate to realtime only if the owner asks follow-up questions.
- **latency:** Start immediately on a button press; complete in 120 seconds, with a first-pass verdict in 10 seconds and detailed measurements afterward.
- **cost:** Near-zero model cost; mostly local serial I/O and a small durable diagnostic report.
- **security:** The test must not open the microphone unexpectedly or upload raw audio. Use generated tones, loopback checksums, and explicit capture indication; retain only counters, hashes, and timing. Require an explicit button press because it exercises audio hardware.
- **missing:** A resolved bounded USB serial diagnostic tool for the two known port families; A deterministic bench-test protocol shared by nRF9160 firmware, ESP32 bridge firmware, and Mac harness; A relay route to publish a signed diagnostic report and correlate it with the pendant status beacon; A dashboard view that distinguishes transport failure from codec/speaker/button failure

### "If a browser task hits a login, CAPTCHA, approval prompt, or missing human decision, pause it and tell me on the pendant exactly what I need to do; once I finish in the browser, resume the safe remainder without starting over."
- **useful because:** Authenticated browser work is where automation currently stops at the worst moment. The owner should not have to remember which tab, job, or step was waiting. The browser sees the private challenge, the Mac keeps the workflow state, the relay waits while everything else sleeps, and the pendant is the one notification channel the owner cannot miss.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard-ux
- **model tier:** Deterministic page-state and command correlation first; use a cheap background model to turn the challenge into one short instruction. Realtime is reserved for an interactive clarification after the owner speaks.
- **latency:** Detect and notify within 2 seconds of a blocked browser command; resume within 5 seconds of the extension's completion signal.
- **cost:** Usually zero model calls for detection and resume; one small summarization call only for ambiguous challenge text. Main cost is browser/session polling.
- **security:** Never send passwords, CAPTCHA answers, or page secrets to the relay/model. Classify challenge type locally, send only origin/title and a redacted instruction, and bind the resume token to the exact browser session, tab, command, and expiry. Do not auto-submit an approval the owner has not explicitly completed.
- **missing:** A first-class blocked-step state in browser command records with reason enum and exact resume cursor; A pendant notification/result channel that carries a short-lived resume token without exposing page contents; A browser heartbeat acknowledgement that distinguishes human completion from mere tab activity; Cross-job correlation joining browser command IDs to Mac action ledgers and relay turn IDs

### "Let me ask the pendant, “What am I looking at?” and get a useful answer about my Mac screen or private browser tab without sending the screen, page, or credentials to the cloud."
- **useful because:** Sensitive work should still be searchable and explainable when the owner is wearing the pendant. Today the Mac and browser can inspect locally, but there is no privacy-preserving path that turns that local understanding into a spoken answer while keeping raw visual data on the device.
- **path:** pendant → mac-vision → browser-extension → mac-planner → relay
- **model tier:** Run vision/OCR and page interpretation locally on the Mac with a small model where possible; send only a short derived answer to the relay or realtime voice tier. Use realtime solely for the spoken exchange.
- **latency:** Acknowledge immediately and return a short answer in 3–8 seconds; longer visual analysis can produce a progress tone and a later result.
- **cost:** One local inference per question; cloud cost is limited to a short answer or none if local speech synthesis is available. Storage is transient and bounded.
- **security:** Raw screenshots, DOM, clipboard, credentials, and page text must remain on the Mac/browser. The relay receives only an explicit redacted answer and a provenance class. Require an on-device active capture indication and automatic destruction of raw frames after the answer.
- **missing:** A local-only vision query mode with an explicit raw-data retention boundary; A browser redaction layer for password fields, tokens, and unrelated tabs before any derived context leaves the Mac; A pendant request envelope that declares privacy mode and receives only derived text/audio; A provenance receipt proving which local frame/tab state generated the answer

### "Carry out this change everywhere it belongs—update the local project, the authenticated web form, and the generated file—and either leave all three consistent or restore the parts that changed and tell me exactly where it stopped."
- **useful because:** Multi-surface work is currently vulnerable to partial completion: a local edit can succeed while a browser submission fails, leaving the owner to discover inconsistency later. The owner needs a coordinated operation with explicit checkpoints and compensating recovery, not a sequence that merely sounds successful.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard-ux
- **model tier:** Use a cheaper planner to decompose and classify steps; deterministic transaction orchestration handles checkpoints and compensations. Use realtime only for the initial request and final spoken summary.
- **latency:** Immediate dispatch acknowledgement; commit or a precise stopped-state within the task's normal duration. Never wait indefinitely for a browser or Mac step without a pendant progress state.
- **cost:** Low model cost after decomposition; storage for manifests, snapshots, and compensating actions is the dominant resource.
- **security:** Snapshots may contain private files and browser data. Keep them local, encrypt sensitive manifests, and expose only hashes and step names remotely. The owner must be told when a compensation is best-effort rather than guaranteed.
- **missing:** A cross-surface transaction manifest with ordered prepare, commit, compensate, and verify phases; Local snapshot adapters for files and browser form state that do not copy secrets to the relay; A compensation registry for Mac and browser actions with honest partial-failure semantics; A final invariant verifier that checks the local artifact, browser state, and expected hash/value agree

### "Watch the health of the things I rely on—Mac, browser bridge, pendant link, and queued work—and interrupt me only when a change is likely to affect me, explaining what will break and what I can do about it."
- **useful because:** The owner should not have to poll dashboards or discover hours later that the Mac went offline, a browser session expired, or a queued action stalled. A cross-surface sentinel can distinguish harmless telemetry changes from an actionable loss of continuity and give one concise spoken warning.
- **path:** relay → pendant → mac-planner → browser-extension → dashboard-ux
- **model tier:** Use deterministic thresholds and history first; use a cheap background model only to rank correlated symptoms and formulate the explanation. No realtime model for routine polling.
- **latency:** Detect within one polling interval; deliver a compact alert within 10 seconds of a high-confidence failure. Suppress repeats until state changes or the owner asks.
- **cost:** Minimal: scheduled polling and small state records dominate; occasional low-cost summarization for correlated incidents.
- **security:** Health telemetry can reveal location, usage patterns, active sites, and project names. Store detailed history locally, send the relay only an event class and remediation hint, and provide a one-command purge. Never infer personal emergencies from device silence.
- **missing:** A durable per-surface health timeline with baselines and correlation IDs; A policy engine for alert deduplication, quiet hours, escalation, and stale-data truthfulness; A relay-to-pendant alert route that carries age, confidence, and remediation—not just a boolean online state; Cross-surface probes that verify end-to-end work delivery rather than merely process liveness


## What it asked for

### `t24-g7ff` (tool) — mac_usb_serial_diagnostics
- why: The pendant and ESP32 are physically connected today, but the existing grant is unresolved and cannot inspect either serial port. A bounded read-only probe is needed before wiring any bench test or claiming wearable continuity.

```json
{
  "type": "object",
  "properties": {
    "ports": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "/dev/cu.usbmodem00096003658",
          "/dev/cu.usbmodem00096003658A",
          "/dev/cu.usbmodem00096003658B",
          "/dev/cu.usbserial-0287A9CA"
        ]
      },
      "maxItems": 4
    },
    "read_ms": {
      "type": "integer",
      "minimum": 50,
      "maximum": 5000
    },
    "max_bytes": {
      "type": "integer",
      "minimum": 1,
      "maximum": 65536
    }
  },
  "required": [
    "ports",
    "read_ms",
    "max_bytes"
  ],
  "additionalProperties": false
}
```

## Its own summary

Recorded three capabilities the owner cannot have today: privacy-preserving local visual questions through the pendant, transactional consistency across Mac/browser/files with compensation and verification, and a cross-surface reliability sentinel that alerts only on meaningful continuity failures. Each requires new orchestration and evidence semantics rather than merely exposing existing routes.

**Biggest unknown:** Whether the existing browser watch and provenance subsystems already provide enough primitives to implement the reliability and privacy boundaries, since discovery is unavailable this round.

