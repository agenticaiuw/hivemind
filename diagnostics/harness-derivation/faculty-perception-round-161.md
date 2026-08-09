# Harness derivation — faculty-perception — round 161

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **macOS control reachability** — At 2026-08-08T02:44Z the AI Pendant Agent has Accessibility and Screen Recording granted; inputReachability is verified, synthesized events reach the screen, secure input is false, and /ops/status reports permissions.ready=true with no required or optional missing permissions. Safari browser bridge is online with 9 tabs and zero pending commands.
  - evidence: GET /observe and GET /ops/status both returned HTTP 200; /observe inputReachability.status=verified and accessibility.trusted=true, screenRecording=true; /ops/status permissions.ready=true and browserExtension.online=true.
- **continuity snapshot capability** — The granted read_continuity_snapshot tool is not executable in the live inventory: its resolver returned unresolved, nearest routes GET /ops/snapshot and GET /pipeline. Cross-surface continuity therefore still requires separate authenticated reads and cannot yet be treated as one authoritative snapshot.
  - evidence: Direct call to read_continuity_snapshot returned resolution=unresolved with nearestRealCapabilities GET /ops/snapshot score 0.447 and GET /pipeline score 0.443.

## Capabilities it proposed

### "When I say “do it and prove it,” carry out a multi-step task across my Mac and browser, then tell me only what the system can verify actually changed—and give me one spoken undo option if it cannot."
- **useful because:** Today a Mac job can report completion even when the target UI, browser session, or downstream state is wrong. This would turn the newly verified Accessibility/Screen Recording access into a trustworthy contract: execute, inspect the resulting UI/state, correlate the browser receipt, and distinguish verified change from mere dispatch.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime for the short voice exchange; cheaper background model for planning and comparing before/after evidence.
- **latency:** Acknowledge within 1 s; execute and verify within 10–30 s for ordinary Mac/browser tasks, with spoken progress only when a step exceeds 5 s.
- **cost:** About $0.02–$0.15 per task depending on realtime audio and vision steps; screenshots/UI inspection and browser reads dominate.
- **security:** Before/after screenshots and page text can contain secrets; redact passwords and sensitive fields before relay storage, require confirmation for irreversible actions, and never claim success from a Mac receipt alone. Accessibility grants make control powerful, so keep an allowlist and retain an undo receipt.
- **missing:** A single correlation ID joining relay voice turn, Mac action ledger, browser command, screenshot inspection, and final receipt; A standard verification result schema with verified/unknown/failed and evidence references; A policy layer that blocks “success” speech unless post-state evidence matches the requested invariant

### "When I leave my desk, say “save my place”; when I come back, say “what changed?” and hear a compact, time-ordered difference across my open apps, browser tabs, pending Mac jobs, and relay work, with no claim about anything the pendant did not confirm."
- **useful because:** The owner loses context between interruptions, but current continuity is fragmented and completion is routinely mistaken for hearing. A bounded departure checkpoint plus return diff would make the system useful even when the pendant is absent or the relay was unreachable, and would clearly separate observed Mac/browser changes from unknown delivery.
- **path:** pendant → mac-planner → browser-extension → relay → faculty-perception → faculty-judgement
- **model tier:** Cheaper background model builds the checkpoint diff; realtime is used only for the two short voice commands and final spoken summary.
- **latency:** Save in under 2 s; return summary in under 5 s for up to 20 changed items.
- **cost:** About $0.005–$0.03 per checkpoint/diff; storage and local state comparison dominate, with little model work.
- **security:** The checkpoint can reveal private app names, URLs, and job content. Store locally with field-level redaction, encrypt or pseudonymize authenticated URLs, expire checkpoints after 7 days, and require confirmation before reopening or acting on changed items.
- **missing:** A durable checkpoint record with explicit capturedAt, source freshness, and owner-selected scope; Diff logic for Mac foreground/apps, browser tabs, jobs, pipeline states, relay jobs, and permissions using one causal timeline; A spoken renderer that labels observed, inferred, and unknown states and never treats completed as heard

### "Run a “wearable check” from my Mac and tell me whether the pendant, audio bridge, relay, and playback path each passed—not just whether the relay is online—and save a timestamped failure report I can hand to you."
- **useful because:** The live registry currently has only the Mac bridge online; the nRF9160 pendant has never registered, and historical pipeline audio is easy to mistake for current hardware health. A USB-aware bench test would make the real boundary explicit: it can test connected firmware and the ESP32 bridge today, report “not attached” honestly when absent, and reserve relay/playback claims for measured evidence.
- **path:** pendant → mac-terminal → mac-planner → relay → faculty-perception → faculty-action
- **model tier:** Cheaper deterministic diagnostics for serial discovery, firmware telemetry, and relay probes; realtime only for the spoken verdict.
- **latency:** Under 20 s for serial discovery and relay liveness; under 60 s for an audio loopback/codec test.
- **cost:** Near-zero API cost; local serial/audio probes dominate. Optional cloud speech verification adds under $0.02.
- **security:** Serial diagnostics may expose device identifiers and audio metrics; keep raw audio local, upload only counters and hashes, and require explicit confirmation before flashing firmware or changing device state.
- **missing:** A Mac route that discovers the two known USB serial devices and runs read-only firmware/bridge probes; A test protocol with independent stages: serial presence, firmware heartbeat, ESP32 audio loopback, relay authentication, socket delivery, and playback acknowledgement; A durable diagnostic report keyed to one test run, explicitly distinguishing absent, unreachable, passed, and unmeasured

### "Why did you do that? Give me a replayable causal answer that starts with my words, shows the interpretation and policy that selected the action, lists every confirmation and permission check, and ends with the exact reversible change—or says where the chain became uncertain."
- **useful because:** The system can retain action receipts and browser evidence, but the owner still cannot audit the causal chain that converted speech into an external action. This would expose silent reinterpretation, hidden policy choices, and accidental authority without requiring the owner to trust a generic “completed” label.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheaper background model builds the structured trace; realtime only answers the owner’s short audit question.
- **latency:** Trace should be assembled in under 3 seconds for a recent action and under 10 seconds for a multi-step job.
- **cost:** About $0.005–$0.04 per audit; most cost is summarizing stored trace nodes, not new inference.
- **security:** The trace may contain private speech, page content, and credentials-adjacent metadata. Redact secrets at write time, keep raw speech local, distinguish model inference from observed facts, and require owner confirmation before exposing sensitive trace details.
- **missing:** An append-only causal trace schema with speech hash, interpretation, policy decision, confirmation, permission, action, observation, and undo edges; Trace emission at relay planning, Mac execution, browser command dispatch, and post-action observation; An owner-facing query that can render uncertainty and distinguish observed state from model rationale

### "Before you tell me something is done, compare the claims from every surface and tell me if they disagree—for example, the Mac says it clicked, the browser says the page is unchanged, or the relay says delivered while the wearable has no playback evidence."
- **useful because:** Today each surface can be locally truthful while the overall conclusion is false. A contradiction detector would catch stale tabs, lost relay deliveries, stale device registry entries, and Mac-side completion that never became a real-world result—the perception gap that matters most to the owner.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Deterministic comparisons first; a cheaper model clusters and explains contradictions; realtime speaks only the concise verdict.
- **latency:** Under 5 seconds after a job completes; continuously updated contradiction state should lag source events by under 2 seconds.
- **cost:** Near-zero for typed state comparisons; roughly $0.005–$0.03 when explanation or visual comparison is needed.
- **security:** Cross-surface state can expose private URLs and app content. Keep raw evidence local, send only typed hashes/statuses to the relay, and never resolve a contradiction by guessing or silently retrying an external action.
- **missing:** A shared event envelope with source timestamp, observedAt, freshness, confidence, and correlation ID; Typed contradiction rules spanning Mac receipts, browser post-state, relay delivery, and eventual wearable playback; A final-state gate that downgrades completion to conflicted/unknown and routes it to the owner instead of speaking success

### "Keep my private data on this Mac: before any browser page, screenshot, audio, or document leaves the device, show me what would cross the boundary, remove secrets and unrelated content, and block the action if the redaction is not trustworthy."
- **useful because:** The owner cannot today see or control the exact data crossing between the browser, Mac, relay, and model. Existing redaction is attached to some evidence paths, but it is not a universal preflight gate for screenshots, page reads, audio, and action context. This would make powerful cross-surface automation safe enough for private accounts.
- **path:** browser-extension → mac-vision → mac-planner → relay → pendant → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Local deterministic classifiers and secret-pattern detection first; a local/cheaper model reviews ambiguous regions; realtime is not needed except to ask for consent.
- **latency:** Under 300 ms for known-secret checks; under 2 seconds for an ambiguous screenshot/page review before dispatch.
- **cost:** Usually below $0.01 per transfer; local classification dominates and avoids sending rejected payloads to a model.
- **security:** The classifier itself must not upload the material it is deciding about. Keep raw data local, use fail-closed behavior for uncertain sensitive regions, make consent scoped to destination and purpose, and retain only redaction metadata and hashes.
- **missing:** A universal egress interception point covering browser results, vision screenshots, audio, and relay tool arguments; A common sensitivity taxonomy and fail-closed redaction envelope consumed by every surface; A user-visible preview/consent protocol with immutable record of what was allowed, withheld, or blocked


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: causal replay of why an action happened, cross-surface contradiction detection that blocks false completion, and fail-closed privacy egress control with owner-visible redaction. Each requires new connective contracts despite existing individual routes.

**Biggest unknown:** Whether any of these overlap with an unexposed backlog item beyond the recorder's similarity checks; all three were accepted as new this round.

