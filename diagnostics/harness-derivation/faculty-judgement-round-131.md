# Harness derivation — faculty-judgement — round 131

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I tap the pendant during a meeting, remember that moment. Afterward, tell me the decisions, action items, and who owes what, with the exact audio/text evidence, then draft (but never send) the follow-ups.”"
- **useful because:** Meetings create obligations faster than the owner can write them down. A private tap is a low-friction marker; post-meeting reconciliation turns fleeting speech into reviewable work without silently contacting anyone.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for transcription and extraction; realtime only for the short spoken confirmation
- **latency:** Tap acknowledgement under 500 ms; post-meeting brief within 10 minutes of the Mac reconnecting or meeting ending.
- **cost:** ~$0.03–$0.20 per meeting depending on local-vs-cloud transcription; browser/Mac extraction and storage dominate latency, not model tokens.
- **security:** Meeting audio is highly sensitive and should remain on the Mac by default; upload only marked clips with explicit per-meeting consent. Never send drafts without confirmation; show source snippets and participant uncertainty.
- **missing:** local meeting-audio capture/transcription with explicit consent and retention controls; a pendant marker event that survives disconnect and syncs over USB today; speaker/participant resolution across Calendar and browser pages; a review UI grouping evidence, decisions, and draft follow-ups

### "“Before any sensitive form, message, or purchase is submitted, show me exactly which fields will leave my browser, redact anything unnecessary, and let me approve the final payload with one physical pendant tap.”"
- **useful because:** The owner can delegate browser work without surrendering secrets. This is stronger than a generic confirmation: it minimizes disclosure, explains each field, and makes the wearable the unmistakable final consent surface.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background classifier for field sensitivity and minimization; realtime only to read a concise diff and collect the tap.
- **latency:** Under 3 seconds to produce a field-by-field diff after a page is ready; submission only after a tap valid for that exact payload.
- **cost:** ~$0.01–$0.05 per staged transaction; DOM extraction and local classification dominate. No cloud model needed for common patterns.
- **security:** Sensitive values must never enter model prompts or logs; use hashes/type labels and local redaction. Bind approval to tab ID, URL, payload hash, and short expiry to prevent replay or confused-deputy attacks. Purchases, deletion, and messages remain confirmation-gated.
- **missing:** local sensitive-field classifier and redaction engine; physical pendant tap/hold event exposed to the relay over USB and eventually LTE; browser bridge support for staged payloads and DOM diffs; a cryptographically bound approval token consumed by the action executor

### "“Teach me one useful personal shortcut each week: notice a repetitive sequence I approved across my Mac and browser, show me the proposed macro and its safety boundaries on the pendant, and install it only when I say yes.”"
- **useful because:** The system should get easier to use over time without silently increasing autonomy. Turning repeated approved work into explicit, inspectable shortcuts gives the owner compounding leverage while preserving control.
- **path:** mac-planner → mac-terminal → browser-extension → relay-realtime → pendant → dashboard
- **model tier:** background analysis of receipts and action traces; realtime only for the spoken suggestion and owner response.
- **latency:** Weekly suggestion can take minutes; invoking an installed shortcut should acknowledge in under 1 second and report completion asynchronously.
- **cost:** <$0.05 per weekly mining pass with local aggregation; model cost is small compared with storing and replaying traces.
- **security:** Mine only reversible, owner-approved actions; exclude secrets, free-form typing, messages, purchases, and destructive operations by default. Show every step, required accounts, and a dry-run result. Store traces locally with bounded retention.
- **missing:** receipt-to-sequence mining across Mac and browser action logs; a typed macro format with preconditions, allowed targets, stop conditions, and dry-run mode; pendant-friendly review/approval of macro boundaries; versioning, rollback, and regression tests when websites or apps change

### "“When I tap the pendant while reading or listening, save the exact text or page fragment I’m on with a short voice annotation. Later, let me say ‘put that in my notes’ or ‘send that to this draft’ and insert the cited fragment into the right Mac or browser surface.”"
- **useful because:** The owner can move knowledge between the physical moment and the right digital destination without copying, switching apps, or losing where it came from. This is a genuine wearable-to-browser-to-Mac handoff, not another summary.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Realtime only for the short annotation and destination clarification; background for fragment normalization and citation packaging.
- **latency:** Capture acknowledgement under 500 ms; later insertion under 5 seconds once the destination is identified.
- **cost:** <$0.03 per capsule when text is locally extracted; browser DOM capture and citation storage dominate.
- **security:** Capsules may contain private page content. Encrypt at rest, bind them to the originating tab/session, expire by default, and require confirmation before inserting into an external message or document.
- **missing:** browser selection/accessible-fragment capture API; a durable encrypted capsule format carrying source URL, tab ID, timestamp, fragment hash, and annotation; Mac insertion adapters for Notes, VS Code, Mail drafts, and browser text areas; a pendant command for listing and choosing recent capsules

### "“When two of my sources disagree—like Calendar versus an email or a browser reservation—do not silently pick one. Bring me a tiny conflict card with the competing evidence, what decision expires first, and one recommended resolution I can accept by voice.”"
- **useful because:** The owner needs help with ambiguity, not just retrieval. Surfacing conflicts at the moment they matter prevents missed meetings, double bookings, and wrong travel or account actions while keeping the final judgement human.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Background evidence collection and conflict ranking; realtime only to present the short card and capture the owner's resolution.
- **latency:** Detect within 2 minutes of a watched source changing; spoken card under 20 seconds; resolution propagated within 5 seconds.
- **cost:** ~$0.02–$0.10 per conflict; source polling and normalization dominate, with small model usage for ranking.
- **security:** Show source URLs, timestamps, and quoted evidence; do not infer a commitment as fact when confidence is low. Never modify calendar, reservations, or messages without explicit approval.
- **missing:** cross-source entity/time normalization; a conflict object with evidence, expiry, confidence, and resolution state; change triggers from authenticated browser watches and Mac calendar/mail; voice-resolvable updates with before/after receipts

### "“Before I send or commit to something important, run a private adversarial check: wrong recipient, stale attachment, conflicting dates, suspicious payment details, or a promise I cannot keep. Show me only concrete risks and the evidence; do not change anything.”"
- **useful because:** A fast second opinion catches the mundane, high-cost mistakes humans make when rushing. It uses the browser, Mac context, and wearable review surface together while preserving the owner's final decision.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background local inspection for documents, calendar, and page state; realtime only for the concise risk readout.
- **latency:** Under 8 seconds for an email/document already open; up to 60 seconds for cross-source checks.
- **cost:** ~$0.02–$0.12 per check; local extraction is cheap, while cross-source reconciliation and OCR increase cost.
- **security:** Keep document contents local whenever possible, redact secrets from prompts, and never contact anyone or alter the draft. Clearly distinguish detected evidence from speculation.
- **missing:** a read-only cross-surface snapshot of the active draft, attachments, recipient, calendar, and relevant browser page; deterministic checks for dates, recipients, attachment freshness, and payment/account changes; a risk report with source citations and confidence rather than a generic model opinion; a single spoken command routed to the current Mac/browser context


## Changes it proposed to its own stack

### `firmware` — Add a durable 'meeting marker' event to the nRF9160 button path: on a short press while a conversation is active, write a 32-byte event (monotonic timestamp, session ID, sequence, marker type, CRC) to a tiny append-only SD/flash journal and emit it over USB immediately; LED gives a distinct two-flash acknowledgement. Replay unacknowledged markers after reconnect, then compact the journal.
- **owner gets:** A private tap lets the owner mark 'that mattered' without interrupting a meeting or speaking aloud, and the marker cannot disappear when LTE/USB drops.
- effort: Medium: firmware event journal, USB framing, relay ingestion, and a small Mac test harness.  ·  risk: Button ambiguity with end-conversation; use long-press for end and debounce/sequence IDs. Corrupt journals are recoverable by CRC and compaction.
- cost: Negligible API cost; firmware uses under 4 KB RAM and a few KB flash. No new hardware because the single button and SD are present.  ·  latency: LED acknowledgement <100 ms; USB delivery on the next serial frame.
- security: Markers contain no audio or content, only opaque session IDs and timestamps; erase with session retention.
- depends on: meeting marker capability and a typed pipeline event schema

### `browser-harness` — Implement a local payload firewall between browser planning and execution: extract candidate form fields, classify each as required/optional and sensitivity tier, generate a canonical payload hash plus a minimized payload, and require an approval token bound to tabId, URL, DOM revision, payload hash, and expiry before irreversible submit.
- **owner gets:** The owner can safely say 'fill this out' knowing the system will not leak an unnecessary phone number, secret, or account detail—and can see exactly what will leave the browser before tapping approve.
- effort: Large: browser bridge protocol, DOM mutation snapshots, local classifier, executor gate, and dashboard diff UI.  ·  risk: Websites mutate between review and submit; hash binding rejects stale approvals and falls back to re-review. Classifier mistakes must default to withholding, not sending.
- cost: Low recurring model cost if classification is local; moderate engineering cost and a few hundred bytes per staged transaction for hashes/evidence.  ·  latency: Adds 1–3 seconds before submit; prevents expensive/reputational mistakes.
- security: Strongly positive: raw sensitive values stay local and logs store labels/hashes, not values.
- depends on: capability field diff and physical pendant approval event

### `model-routing` — Create a background 'routine miner' that consumes only completed Mac/browser receipts, clusters repeated reversible action sequences, and emits one weekly macro candidate with a dry-run trace and explicit exclusions. Never invoke realtime for mining; retain only normalized action types and target classes, not typed content.
- **owner gets:** The system compounds: repetitive chores become one spoken shortcut, while the owner keeps control over exactly what the shortcut may touch.
- effort: Medium-large: receipt normalization, sequence mining, macro DSL, dry-run executor, and weekly review delivery.  ·  risk: Overgeneralized macros could act on the wrong account or changed UI; require stable target fingerprints, preconditions, dry-run, and automatic disablement on mismatch.
- cost: A few cents or less per weekly pass; storage is bounded by normalized traces and 30-day retention.  ·  latency: No interactive impact; weekly analysis can run overnight.
- security: Positive if content is excluded and candidates are never auto-enabled; macro scopes must be least privilege.
- depends on: typed cross-surface receipts and explicit macro approval UI

### `hardware` — Replace the prototype's single-button/single-LED control with a wearable control cluster: a distinct mark button plus a recessed stop/privacy button, a small haptic motor, and a hardware mute indicator. Preserve USB serial compatibility and make stop/privacy electrically local so it works with no relay or Mac.
- **owner gets:** The owner gets a reliable, silent way to mark information, stop recording, or guarantee privacy in a meeting, street, or noisy room—without confusing 'mark' with 'end' and without trusting software to notice a command.
- effort: Large hardware revision: enclosure, GPIO/firmware changes, battery and EMC validation, haptic driver, and a clear interaction specification.  ·  risk: More controls can increase accidental presses and power draw. Use recessed/long-press stop, tactile differentiation, boot self-test, and a visible mute state; retain the current button mapping during transition.
- cost: Roughly $3–$8 in components and under 20 mA peak haptic draw; negligible API cost.  ·  latency: Hardware stop/mute is immediate; richer acknowledgement avoids waiting for audio or relay round trips.
- security: Strongly positive: a physical privacy cutoff is enforceable offline and auditable in firmware.
- depends on: meeting-marker event protocol; pendant firmware state machine and enclosure redesign


## What it asked for

_Nothing._
