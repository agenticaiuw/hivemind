# Harness derivation — relay-realtime — round 135

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Capture what I just said as an evidence capsule and file it for me.”"
- **useful because:** The owner can speak a quick observation or instruction while away from their Mac. The system turns it into a durable, searchable artifact with source context (active tab/app, timestamps, optional web snapshot) so they can act on it later without losing the moment.
- **path:** pendant → relay → mac-planner → browser-extension → mac-bridge
- **model tier:** Realtime for immediate confirmation; a cheaper planning tier on the Mac to assemble the capsule and write it to disk/reminder.
- **latency:** Under 1–2 seconds to acknowledge capture; tens of seconds is acceptable for assembling sources and writing files/reminders.
- **cost:** Low per invocation at relay; dominated by downstream Mac planning and browser extraction if needed.
- **security:** Captures may include sensitive content from the mic and active browser tabs. The owner should get a clear confirmation of what was captured and where it was stored, and optionally require confirmation before attaching browser page extracts.
- **missing:** A working relay intent routing implementation (relay_route_intent); A durable job runner or queue on the relay so capture survives brief disconnects; A standardized evidence capsule format and storage location in the Mac workspace

### "“What is actually current right now?” — give me one trustworthy spoken situational brief that reconciles my pendant, Mac, and authenticated browser instead of repeating conflicting statuses."
- **useful because:** Today the owner can receive mutually inconsistent facts (for example, the browser’s active URL can disagree with its durable session title, and timezone sources can disagree). A worn-device answer should distinguish fresh evidence from stale metadata, say what is uncertain, and avoid making an action on the wrong tab, account, or location. This only works by combining the pendant/relay’s live voice context, Mac telemetry, and browser-held session evidence, then having perception establish truth before judgement speaks.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use relay-realtime only to ask the short clarifying question and deliver the final low-latency sentence; use faculty-perception (cheaper background model) to merge and timestamp evidence, and faculty-judgement to rank contradictions and decide what can safely be stated.
- **latency:** Owner hears an acknowledgement in under 500 ms and the reconciled brief within 3–5 seconds; stale sources should be explicitly labeled rather than blocking indefinitely.
- **cost:** Roughly one realtime turn plus two small background inference calls per request; the dominant cost is resending evidence snippets, so send typed deltas and hashes rather than full histories.
- **security:** Browser evidence may contain email, names, and private URLs. Keep extraction on the authenticated browser bridge, transmit only the minimum cited fields to the relay, redact tokens/page bodies by default, and never claim a source is current without a freshness timestamp. No mutation or approval gate is needed for this read-only capability.
- **missing:** A shared typed evidence envelope with source, observed_at, freshness, scope, and confidence; A relay fan-in endpoint that snapshots Mac and browser state for one correlation id; Contradiction resolution rules owned by faculty-perception/judgement; A spoken citation format and persisted audit record showing which sources supported the answer

### "“What am I looking at on my computer right now, and what are the two most important things on it?”"
- **useful because:** A pendant owner cannot see the unattended Mac screen, and browser DOM alone misses native apps, dialogs, notifications, and visual state. A synchronized Mac screenshot/accessibility snapshot plus authenticated browser extraction lets the owner ask a genuinely remote, hands-free situational question and receive a concise prioritized answer without asking the system to click anything.
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use mac-vision’s inexpensive vision loop for screenshot/accessibility extraction, browser-extension extraction for DOM/session facts, faculty-perception to merge the two modalities, and relay-realtime only for the short spoken response.
- **latency:** Acknowledge immediately; deliver the answer in 4–8 seconds. If screen capture is unavailable, say so and answer only from browser evidence rather than fabricating native-app state.
- **cost:** One small screenshot/vision inference plus one compact browser extraction and a short realtime synthesis; screenshot transfer and vision tokens dominate cost. Downsample and crop to the active window where possible.
- **security:** Screens may contain passwords, private messages, or unrelated work. Capture only the active display/window, redact known secret fields, keep raw screenshots on the Mac, send OCR/structured findings rather than pixels by default, and expire the correlated evidence. This is read-only and needs no confirmation.
- **missing:** Re-enable or replace the currently disabled mac-vision computer-use loop with a read-only screenshot/accessibility sampler; A Mac endpoint that returns active-window identity and redacted visual findings without exposing raw screenshots; A common multimodal evidence envelope shared with browser extraction and faculty-perception; Relay voice orchestration that can fan in both results and state limitations


## Changes it proposed to its own stack

### `integration` — Build a read-only situational-truth fan-in service keyed by correlation ID. On a voice request, it concurrently snapshots /machine-context, /ops/status, browser inspections/session metadata, and Mac status; normalizes each observation into {source, scope, observedAt, expiresAt, value, confidence, redactions}; computes contradictions without silently choosing one; sends the compact evidence set to faculty-perception, then faculty-judgement returns a ranked answer and explicit unknowns. Store the source references and resolution in a short-lived audit record that relay-realtime can turn into a spoken brief.
- **owner gets:** When the owner is away from the Mac, they get a dependable answer about what is really open, current, or available instead of an overconfident answer assembled from stale browser titles, old machine context, or a disconnected Mac. It prevents acting on the wrong authenticated tab while remaining entirely read-only.
- effort: Medium: one relay integration endpoint, a small evidence schema/TTL store, concurrent adapters for existing status routes, and perception/judgement prompt contracts. Add fixture tests for stale, missing, and contradictory sources.  ·  risk: A source can fail or leak more content than intended; fail closed to “unknown” for missing evidence, redact URLs/query strings and page text by policy, bound payload size, and retain only hashes plus selected fields. Recovery is simply retrying the snapshot with a new correlation ID; no Mac or browser mutations occur.
- cost: No new paid service. One compact background perception call and one judgement call per request; typed deltas and source hashes reduce repeated context. Short-lived records have negligible storage cost.  ·  latency: Parallel collection should add about 0.5–2 seconds, with an immediate spoken acknowledgement while reconciliation runs. Slow or offline surfaces are reported as stale rather than holding the voice channel indefinitely.
- security: Read-only least-data projection between browser/Mac and relay; authenticated browser content never gets copied wholesale. Correlation records must have owner-scoped access and automatic expiry.
- depends on: A shared evidence-envelope schema and freshness policy; A relay fan-in route able to read existing /ops/status, /machine-context, and browser inspection/session routes; Faculty-perception and faculty-judgement contracts for contradiction reporting; A compact spoken-citation renderer in relay-realtime

### `mac-harness` — Add a read-only active-context snapshot endpoint on the Mac that atomically returns the frontmost app/window, accessibility tree summary, and a privacy-filtered downsampled screenshot or OCR regions, with capture timestamp and an explicit unavailable reason. Keep raw pixels local; expose only the selected window and structured findings to the relay’s correlation ID. Do not enable clicking or typing as part of this change.
- **owner gets:** The owner can ask the pendant what is currently on the unattended Mac and get an honest answer that includes native apps and dialogs, not just whichever browser tab happens to report metadata. It also gives the hive a reliable visual source when browser and Mac status disagree.
- effort: Medium: implement a read-only harness adapter, active-window selection, redaction/cropping, bounded screenshot transport, and tests for Accessibility/Screen Recording being false. The current Mac reports those permissions false, so installation must surface the exact missing permission and degrade cleanly.  ·  risk: Screens can contain highly sensitive data or the wrong monitor. Never capture background windows, cap image size, redact password fields, expire payloads, and return unavailable rather than guessing when permissions or focus are ambiguous. No mutation path is added.
- cost: Small implementation/storage cost; vision inference becomes the recurring cost only when the owner asks. Cropping and OCR reduce transfer and token cost.  ·  latency: Target 1–3 seconds for capture and serialization; vision interpretation adds several seconds. Immediate spoken acknowledgement handles the wait.
- security: New screen-data surface is sensitive. Owner-scoped authentication, in-memory processing, no durable raw screenshots, audit hashes only, and strict TTL are required.
- depends on: macOS Accessibility and Screen Recording permission or an approved alternative capture mechanism; Read-only mac-vision loop (currently disabled); Shared evidence envelope/fan-in integration; Redaction policy for screen and OCR output


## What it asked for

_Nothing._
## Its own summary

Recorded three non-duplicate items: (1) a spoken cross-surface situational-truth brief that reconciles fresh Mac/browser/pendant evidence and exposes contradictions, (2) the integration fan-in/evidence-envelope and freshness ledger required to make that reliable, and (3) a remote “what am I looking at?” capability plus a read-only Mac active-window/screenshot sampler, since browser metadata cannot describe native UI. The owner still cannot have these today because there is no shared evidence contract/fan-in, and mac-vision capture is disabled with Accessibility/Screen Recording unavailable.

**Biggest unknown:** Whether the Mac can be granted the required read-only Accessibility/Screen Recording permissions (or provide an equally trustworthy active-window snapshot) without violating the owner’s privacy and unattended-Mac expectations.

