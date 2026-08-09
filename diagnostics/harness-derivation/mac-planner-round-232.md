# Harness derivation — mac-planner — round 232

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-and-screen-recording** — Live Mac status now reports Accessibility trusted, Screen Recording granted, and ui actions will reach the screen from AI Pendant Agent; the earlier owner-blocked assumption is obsolete.
  - evidence: GET /observe at 2026-08-08T22:49:43.608Z returned accessibility.trusted=true, screenRecording=true, inputReachability.status=verified; GET /ops/status returned requiredMissing=[] and ready=true.

## Capabilities it proposed

### "When I press the pendant's bookmark button, save exactly what I was doing on the Mac so I can say 'resume that' later."
- **useful because:** The current bookmark survives as a timestamp, but a timestamp does not recover a half-written draft, the browser page, or the active project. This would turn an interruption into a durable, searchable handoff without recording ambient audio by default.
- **path:** pendant → mac-vision → browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Use the realtime model only for the spoken command and acknowledgement; use a cheaper background model to summarize and deduplicate the captured context.
- **latency:** A local Mac/browser snapshot and pendant acknowledgement within 1 second; capsule synthesis within 5 seconds after the link is available.
- **cost:** About $0.01-$0.04 per handoff, dominated by one background summarization call; raw snapshot capture is local and free.
- **security:** Capture only foreground app, active tab URL/title, selected text when explicitly available, project path, and a redacted 1-2 sentence state summary. Never capture passwords, page bodies, microphone audio, or secrets by default. Creating a capsule is safe; reopening an app or submitting an edit still follows the owner's action policy.
- **missing:** A semantic Mac read route for current document identity, selected text, and active editor project (the existing observation route gives app/browser identity but not document state); A relay data model and retrieval command for interruption capsules; A pendant event field linking offline_moment_bookmark records to the captured capsule

### "I lost the thread—find the last thing I was working on across my pendant bookmarks, browser, calendar, mail, and Mac, then open the right place and tell me the next action."
- **useful because:** The owner currently has separate timestamps, browser sessions, mail/calendar briefs, and Mac jobs. This is the missing retrieval operation: reconstruct intent from several weak signals instead of forcing him to remember which surface held it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → unified
- **model tier:** Use a small background model to rank and cluster evidence; reserve realtime for the final one-sentence spoken answer and any follow-up question.
- **latency:** Return a ranked candidate in 3 seconds and open the selected non-destructive location within 5 seconds; ask instead of guessing when confidence is low.
- **cost:** Roughly $0.01-$0.03 per query; local source reads dominate latency, not tokens.
- **security:** Search snippets and metadata by default, redact message bodies and secrets, and never infer or expose secret captured facts. Opening a file or URL is reversible; sending, deleting, or editing remains outside the retrieval operation.
- **missing:** A relay-side federated search/index over bookmark events, capture records, Mac jobs, and browser capsules; A stable correlation ID shared by pendant bookmarks, browser commands, and Mac job receipts; A read-only semantic document/project identity from the Mac editor

### "Make the change I just described, test it, and give me a spoken result with the exact files and evidence—whether I am talking about code in VS Code, a browser workflow, or a document."
- **useful because:** Today the system can act on the Mac or browser, but the owner must manually stitch together planning, execution, test output, and the answer. This would make the hive a trustworthy execution loop: understand on the pendant, act on the Mac/browser, and report proof rather than merely claiming completion.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → mac-terminal → unified
- **model tier:** Realtime handles intent clarification and the final short spoken report; a cheaper background model decomposes the task, reads bounded test output, and summarizes evidence.
- **latency:** A plan preview in 2 seconds, execution as long as the actual task requires, and a spoken receipt immediately after each durable step; long jobs must survive a dropped link.
- **cost:** About $0.03-$0.15 per task, dominated by vision/browser observations and background summarization; local execution and receipts are free.
- **security:** Every step gets an immutable touched-resource and result receipt. The system must not claim tests passed without captured exit/status evidence. File deletion, sending mail, purchases, and external submissions remain explicit confirmation points; secrets and full page contents are redacted from the spoken report.
- **missing:** A single cross-surface job graph joining mac_action_preflight, browser command IDs, Mac receipts, and workbench transaction receipts; Bounded test/result capture with exit status and artifact hashes (the current FULL_CONTROL shell receipt is not sufficient); A relay protocol for streaming progress and final evidence to the pendant inbox without replaying duplicate steps

### "Answer sensitive questions privately: put confidential details only in my ear, while showing harmless summaries on the Mac, and never echoing secrets into the browser or shared notifications."
- **useful because:** A privacy latch stops capture, but it does not prevent a valid answer from leaking through the wrong output surface. This gives the owner useful assistance in a room with other people: the pendant is the private channel, while Mac/browser surfaces receive only a redacted acknowledgement.
- **path:** relay-realtime → pendant → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Use the realtime model for intent and response generation; use a small local policy/classification model for output routing and redaction so raw secrets do not leave the relay unnecessarily.
- **latency:** Choose a route before the first response token; private audio and a redacted screen update should begin within 2 seconds.
- **cost:** About $0.01-$0.05 per sensitive response, mostly the response generation; redaction and routing are local or relay metadata operations.
- **security:** Default to private-only when confidence is uncertain. Apply structured secret detectors and never send the unredacted answer to the Mac/browser. Keep an auditable routing receipt containing classifications, not secret content. Require explicit owner action to copy or display a secret.
- **missing:** A relay output-policy contract that labels each response private, redacted, or public; A Mac/browser sink that accepts redacted capsules without receiving the private payload; A pendant delivery acknowledgement and timeout fallback so a private answer is not silently shown elsewhere

### "When something fails, tell me why in one sentence and offer the smallest safe repair—using pendant audio quality, relay state, Mac jobs, browser commands, and the exact evidence instead of making me debug each surface."
- **useful because:** The owner currently gets isolated failures from separate nodes. A causal incident answer would turn 'it failed' into an actionable diagnosis, such as stale browser command, dropped audio delivery, or a Mac job that never started, while avoiding a dangerous blind retry.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Use a cheap background model or rules engine for correlation and diagnosis; use realtime only to phrase the final sentence and ask for authorization when repair mutates state.
- **latency:** Detect within 2 seconds of a failed receipt or QoS alert; speak diagnosis immediately and produce a repair plan within 5 seconds.
- **cost:** About $0.005-$0.03 per incident, dominated by optional summarization; correlation over receipts and counters is local.
- **security:** Evidence should be bounded, hashed, and redacted before model use. Never retry a deletion, purchase, message send, or external submission automatically. Every proposed repair needs an idempotency key and an explicit distinction between observed facts and inference.
- **missing:** A normalized incident envelope joining audio QoS, relay jobs, Mac receipts, and browser command results; Machine-readable failure codes and exit statuses for all action types; An idempotent repair planner with dry-run output and a durable causal/evidence receipt

### "What changed since I last checked? Compare the Mac screen, active browser work, calendar/mail signals, and pendant events, then tell me only the changes that require my attention."
- **useful because:** A snapshot tells the owner what is true now; it does not tell them what changed while they were away. A cross-surface delta lets the owner safely resume after a meeting, commute, or dead zone without rereading every app and without turning every notification into an interruption.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension → unified
- **model tier:** Use deterministic local diffs and a cheap ranking model for change detection; use realtime only for the short spoken digest and follow-up questions.
- **latency:** Compute a delta in under 3 seconds from cached baselines; speak a three-item maximum digest in under 5 seconds.
- **cost:** About $0.005-$0.02 per request; source inspection and diffing are local, with a small summarization call only when needed.
- **security:** Keep baselines encrypted and expire them. Compare metadata and redacted snippets by default, never full mail bodies or sensitive page content. Suppress low-confidence changes and provide source labels so the owner can inspect rather than trust an opaque summary.
- **missing:** A durable, privacy-filtered baseline per surface with explicit timestamps and owner-controlled retention; Semantic diffs for Mac UI/document state and browser page state rather than pixel-only comparison; A relay query that joins deltas with pendant bookmarks and ranks urgency without replaying already acknowledged events


## Changes it proposed to its own stack

### `hardware` — Add a low-power BLE companion MCU and a small protected LiPo/USB-C power-management path to the pendant carrier, with a framed local transport for bookmark events, alert receipts, QoS telemetry, and staged audio metadata. Keep LTE/audio on the existing nRF9160 and make BLE a store-and-forward side channel to the Mac when cellular is unregistered or USB is absent.
- **owner gets:** The owner can wear and use the pendant in the real world instead of only while tethered to a bench Mac or waiting for LTE registration. Nearby Mac connectivity would make bookmarks and alerts arrive promptly in dead zones, while cellular remains the long-range path.
- effort: Medium-high: new carrier schematic/layout, BLE firmware, authenticated pairing, power characterization, and relay/Mac bridge integration; 4-8 weeks for a reliable prototype.  ·  risk: A second radio can create pairing/security bugs and RF or audio interference. Recover by keeping the existing LTE path authoritative, buffering idempotent events, and allowing BLE to be disabled. Do not expose raw microphone audio over an unpaired link.
- cost: Approximately $8-$20 in prototype BOM (BLE MCU, PMIC, battery protection, antenna/layout changes), plus roughly 5-25 mA active and <100 uA sleep depending on the selected MCU.  ·  latency: Nearby event delivery could fall from dead-zone/unregistered to sub-second; audio should remain on LTE/USB until BLE throughput and coexistence are measured.
- security: Requires per-owner authenticated pairing, rotating session keys, replay protection, and a physical unpair/reset path. BLE must carry typed encrypted frames, not arbitrary Mac commands.
- depends on: A defined BLE frame protocol shared by pendant firmware, Mac bridge, and relay; Owner pairing UX and key recovery; Bench RF/audio coexistence testing


## What it asked for

### `t22-e6k4` (tool) — mac_semantic_context_read
- why: The three cross-node capabilities above need the current editor document/project and selected text, not just foreground app and browser URL. Without this, interruption recovery and evidence reports guess at what the owner was doing.

```json
{
  "type": "object",
  "properties": {
    "operation": {
      "type": "string",
      "enum": [
        "document_identity",
        "selected_text",
        "editor_project"
      ]
    },
    "app_scope": {
      "type": "string"
    },
    "max_chars": {
      "type": "integer",
      "minimum": 1,
      "maximum": 4000
    },
    "redact": {
      "type": "boolean"
    }
  },
  "required": [
    "operation"
  ]
}
```

## Its own summary

This round produced four non-duplicate deliverables: interruption handoff that binds the existing pendant bookmark to Mac/editor/browser state; federated 'lost the thread' retrieval; an evidence-backed make/test/report loop across Mac, browser, relay, and pendant; and a hardware proposal for BLE store-and-forward when LTE/USB is unavailable. I also queued a precise read-only semantic Mac context tool (t22-e6k4) for document identity, selection, and editor project. Important discovery: Accessibility and Screen Recording are now live and verified, so the old permission blocker is gone. The live Mac, relay, and Safari bridge are all online.

**Biggest unknown:** The remaining critical gap is not permission: it is whether the Mac agent can expose stable, redacted editor/document identity and bounded test exit evidence. Until that exists, cross-node recovery and proof reports must guess or rely on fragile UI snapshots. The BLE proposal additionally needs an owner-approved pairing/power design and a shared frame protocol.

