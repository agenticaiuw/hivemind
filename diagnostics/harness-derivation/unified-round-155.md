# Harness derivation — unified — round 155

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep my conversation alive when LTE drops: transparently move the pendant's live voice session to the USB-connected Mac/ESP32 bridge, then return to LTE at a turn boundary without replaying or losing audio."
- **useful because:** The owner can keep talking instead of restarting after the exact failure that currently makes a wearable feel unreliable. The Mac-attached hardware is real today even though LTE registration is not.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** Realtime for the active turn; deterministic transport state machine and background diagnostics outside speech.
- **latency:** Route decision under 250 ms; no duplicate audio; handoff only at a turn boundary, with at most one buffered 60 ms frame.
- **cost:** Negligible model cost during handoff; roughly 1-2 relay requests per transition. Dominant cost is implementation/testing and a short local buffer, not inference.
- **security:** USB is a local trusted transport only after explicit pairing; never expose raw audio to arbitrary serial devices. Sign each transport transition and include monotonic turn/frame numbers. LTE remains the standalone baseline, not a phone assumption.
- **missing:** Mac bridge transport adapter for the accepted usb_fallback_audio_session; Relay session ownership and turn-boundary handoff protocol; A/B fault-injection test covering simultaneous uplink/downlink loss and reconnection

### "When I am offline, let me ask the pendant for a small local Mac action and have it finish and sync the receipt later: 'make a note of this', 'set a reminder', or 'save this marker', with no claim that cloud work happened until the relay confirms it."
- **useful because:** The owner can still get useful work done while LTE is unregistered or the relay is unreachable. Today the physical device is attached to the Mac, so this is actionable now rather than a hypothetical phone feature.
- **path:** pendant → mac-planner → mac-terminal → relay-realtime
- **model tier:** Realtime only to transcribe/classify the short request; deterministic local intent allowlist and background relay reconciliation.
- **latency:** Acknowledge locally within 1 s; execute only allowlisted reversible/local actions within 5 s; sync receipts opportunistically without delaying the next turn.
- **cost:** Usually one short realtime turn and zero extra model calls for known intents; Mac action and relay receipt storage dominate.
- **security:** Offline mode must be a narrow allowlist (create reminder, append note, timestamp marker), never arbitrary shell/browser/message sending. Show 'queued locally' versus 'confirmed by relay' distinctly; require the physical transaction latch for anything beyond the allowlist.
- **missing:** A durable local intent spool paired with the existing USB audio session; A typed local-only action executor and later relay receipt reconciliation; Explicit owner-configurable offline allowlist and retention/deletion policy

### "Before I leave a task, tell me which of my requested actions are actually complete across the Mac and browser, which are only queued, and which have no evidence; let me approve the remaining staged actions on the pendant instead of trusting a spoken promise."
- **useful because:** The owner gets a truthful stopping point after a complex request: no silent browser no-op, no confusing relay acceptance with physical completion, and no accidental replay after a crash.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Cheap deterministic evidence join first; realtime speech only to summarize the resulting state and accept a physical approval event.
- **latency:** Evidence snapshot under 2 s for up to 20 steps; approval state must be visible locally before execution; no action runs on an incomplete or changed plan.
- **cost:** One read-only evidence join plus at most one short spoken summary; model cost is small, while browser/Mac evidence collection dominates.
- **security:** Bind evidence to exact browser tabs/apps, job IDs, plan digest, world fingerprint, expiry, and the physical transaction nonce. Never treat relay 'accepted' as browser 'submitted'. Redact page contents and secrets from speech and receipts.
- **missing:** Relay implementation of the existing approval handoff contract and delivery/readback path; A cross-surface evidence join over Mac job receipts, browser results, and pendant delivery acknowledgements; Orchestrator ledger closure and a stale-job lease/reconciliation policy before any resume or replay

### "When I ask “what changed since yesterday?”, give me a privacy-filtered, evidence-backed delta across my Mac, browser sessions, and pendant markers: only changes tied to apps/tabs I explicitly allow, with a source and timestamp for every sentence, and an honest 'nothing observed' when there is no evidence."
- **useful because:** The owner gets a reliable personal state change report instead of a model-generated impression. It turns the separate browser, Mac, and worn-device perspectives into one useful answer while preserving the difference between observed, inferred, and unknown.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Deterministic event and receipt join first; use the background tier to summarize a bounded delta, with realtime only for the owner's spoken query.
- **latency:** Return a short answer in under 4 seconds for a 24-hour window; never block the live voice turn on an unavailable surface, and label each source that was offline.
- **cost:** One bounded evidence query and a small background summarization call; storage and indexing of compact metadata dominate, not audio or large page contents.
- **security:** Require explicit app/tab bindings and a per-source retention policy. Store hashes, titles, timestamps, and redacted outcome metadata rather than page contents or ambient audio. Never infer a change from absence of access; say unavailable. Spoken output must omit secrets and sensitive URL parameters.
- **missing:** A cross-surface append-only change index joining Mac job receipts, browser inspection results, and pendant moment-marker events without copying raw content; An owner-facing allowlist and retention/deletion controls for source bindings; A typed delta schema distinguishing observed change, completion receipt, queued work, and unavailable source; A bounded background summarizer that cites source IDs in the spoken response

### "When you give me an answer or recommendation, let me ask “why?” and hear a compact provenance trail: which Mac observation, browser result, pendant marker, or relay receipt supports each claim, what was unavailable, and which parts are inference rather than fact."
- **useful because:** The owner can trust the system without treating fluent speech as evidence. This is especially valuable when browser actions, queued jobs, and wearable delivery disagree.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Deterministic provenance graph and redaction first; cheap background summarization; realtime only to speak the selected trail.
- **latency:** Produce a three-to-five item explanation within 3 seconds; expand only when requested.
- **cost:** Low model cost for a bounded summary. The main cost is maintaining compact signed provenance edges, not retaining raw content.
- **security:** Provenance must inherit the source's sensitivity and access binding. Do not read unrelated tabs or expose secrets merely to explain a result. Every claim should have observed/inferred/unavailable status and an opaque receipt ID.
- **missing:** A typed provenance graph spanning Mac, browser, relay, audio-delivery, and pendant-marker receipts; A redaction policy that can produce spoken-safe evidence snippets without copying page secrets; A claim-to-source response contract usable by the realtime voice path

### "If I say “stop and forget that task,” revoke it everywhere: cancel queued Mac and browser work, invalidate pending physical approvals, suppress its future pendant alerts, and return one receipt proving which surfaces stopped and which could not be reached."
- **useful because:** A single spoken revocation should actually stop a distributed action, rather than leaving a browser command, relay job, or wearable inbox item alive after the owner changed their mind.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Deterministic revocation coordinator; realtime only to disambiguate the target and report the final receipt.
- **latency:** Issue cancellation within 1 second and converge or report unreachable surfaces within 10 seconds; never claim deletion where only suppression was achieved.
- **cost:** No substantial model cost; a bounded fan-out to job, browser, pendant, and relay stores dominates.
- **security:** Require an unambiguous job/task binding and physical confirmation for revoking an already-approved irreversible action. Use tombstones and idempotency keys so reconnecting surfaces cannot resurrect work. Distinguish cancel, suppress, and erase; raw audio and secrets need separate deletion handling.
- **missing:** Cross-surface revocation protocol with durable tombstones and expiry; Adapters for Mac job cancellation, browser command invalidation, relay queue removal, and pendant inbox suppression; A typed convergence receipt that reports stopped, already-completed, unreachable, and erase-pending states


## What it asked for

_Nothing._
## Its own summary

This round recorded three distinct owner-facing capabilities: (1) seamless LTE↔USB conversation continuity at turn boundaries, (2) offline Mac-local allowlisted actions from the physically connected pendant with honest queued-vs-confirmed receipts, and (3) a cross-surface completion/evidence briefing that gates remaining work on the pendant's physical approval. I also discovered the live device state: Safari is online, the home Mac bridge is online, and the cloudflare contract-test device is offline. A proposed relay approval implementation was correctly rejected as a restatement of the already-accepted physical approval path, so I did not rephrase it.

**Biggest unknown:** The remaining blockers are implementation gaps rather than discovery: the USB fallback adapter and transport handoff protocol, a typed local offline-intent spool/reconciler, and the relay-side approval/delivery implementation. I still need an owner decision on retention/deletion policy (already requested and pending), plus actual LTE registration or a repeatable Mac-attached hardware run to validate handoff behavior. I will not re-request denied macOS permissions.

