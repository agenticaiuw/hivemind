# Harness derivation — faculty-judgement — round 161

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take me back to where I left off.”"
- **useful because:** The pendant can mark a moment while away from the keyboard, and the Mac/browser can later reconstruct the actual work context instead of merely remembering a sentence. It turns a physical bookmark into a safe, source-linked resume: active project, foreground app, relevant tabs, and the owner's marker are joined, then presented for review before anything is reopened or changed.
- **path:** pendant → mac → browser → relay
- **model tier:** Background model for periodic context compaction; realtime only to interpret the spoken request and disambiguate which bookmark.
- **latency:** Under 2 seconds to list candidate bookmarks; under 8 seconds to assemble a context card. Reopening tabs/apps is explicit and can take normal browser latency.
- **cost:** <$0.01 per invocation when a stored context card exists; a model call dominates only when several projects/tabs need semantic ranking.
- **security:** Persist opaque marker IDs and redacted titles/digests by default, not page bodies or credentials. Browser sessions may contain private material, so the card must show provenance and require confirmation before reopening authenticated tabs or executing a draft. Expire stale cards and offer one scoped forget operation.
- **missing:** A local USB event that joins sw1's offline_moment_bookmark payload to a Mac capture of foreground app/project/browser session; A durable marker-to-context foreign key (currently the five ID namespaces do not join); A reviewable context-card route and explicit restore operation; do not silently execute browser actions

### "“Give me the brief, but only tell me what I actually heard.”"
- **useful because:** Today a briefing can be generated and queued while the owner never downloads or finishes it. This capability closes the loop: source items become individually addressable, the pendant reports downloaded/started/finished/interrupted, and the relay tells the owner which items remain unheard rather than claiming completion. It prevents missed deadlines hidden behind a successful server receipt.
- **path:** relay → mac → pendant → browser
- **model tier:** No expensive model for delivery accounting; use deterministic itemization and ACK reconciliation. Use the realtime model only for the short spoken status sentence when the owner asks.
- **latency:** ACK ingestion under 200 ms; status response under 1 second from stored events. A missing ACK is reported after a configurable expiry, not guessed immediately.
- **cost:** Negligible inference cost; storage and event processing dominate. One optional short status generation is <$0.005.
- **security:** Artifact IDs and item hashes only in device events; no transcript or source content in the pendant ACK. Deduplicate by event ID and monotonic device sequence, reject events from unknown sessions, and distinguish downloaded from played. A private item's title must not be spoken merely because it is undelivered.
- **missing:** A durable briefing-item manifest with stable item IDs and cursor tokens shared by relay and Mac; A real event-ingestion route wired to the granted record_pendant_delivery_event capability, including offline replay and duplicate suppression; A policy decision for what to do with interrupted/private items (queue, redact, or require owner request); A relay-to-Mac join between pipeline/job IDs and pendant artifact IDs

### "“Move this conversation to my Mac without making me start over.”"
- **useful because:** The pendant is physically USB-attached and testable even while LTE is unregistered. The owner should be able to press the Mac's continuation control and have the local agent receive the current spoken intent, unresolved question, and safe next step, then show a compact handoff in the active editor/browser. This makes the pendant useful in the real failure mode—link loss or walking up to the laptop—without pretending the relay is online.
- **path:** pendant → mac → relay → browser
- **model tier:** Realtime model only to summarize the active exchange into a bounded handoff; deterministic transport and validation everywhere else.
- **latency:** USB handoff acknowledgement under 500 ms; a summarized context card under 3 seconds. No external network dependency.
- **cost:** <$0.01 for a short bounded summary; USB framing, local persistence, and UI confirmation dominate engineering cost.
- **security:** Use a local authenticated USB session and an opaque handoff nonce. Send only the selected turn and redacted intent, never raw microphone buffers, browser cookies, or page secrets. The Mac must display the received context and require confirmation before browser navigation or external side effects. Expire unclaimed handoffs quickly and make them revocable.
- **missing:** A firmware/USB serial handoff message type that can export the active interaction without exporting queued audio; A Mac USB listener that validates device session/sequence and exposes a reviewable handoff card; A real cross-surface correlation ID; current relay, Mac, browser, and action IDs only meet in unindexed telemetry; A local continuation UI/action that can target VS Code or a browser tab without Accessibility-dependent assumptions

### "“Show me the two futures before you do anything: what changes if I approve this, and what stays untouched if I don’t.”"
- **useful because:** The owner currently gets either a plan or an execution, not a comprehensible fork across the Mac, authenticated browser, relay jobs, and pendant. This would produce a bounded counterfactual: files/apps/tabs/messages affected, external recipients, spend or irreversible points, expiry assumptions, and the exact rollback path. It lets the owner make a meaningful decision without exposing secrets to the pendant or triggering a mutation just to learn its consequences.
- **path:** relay → mac → browser → pendant
- **model tier:** A cheap deterministic simulator and policy evaluator should build the change set; use the expensive model only to explain ambiguous dependencies in one short spoken summary.
- **latency:** Read-only state collection under 2 seconds; a full cross-surface comparison under 6 seconds. No mutation is permitted during rehearsal.
- **cost:** Usually <$0.01; browser/Mac reads and diff computation dominate, with model cost only for ambiguous natural-language explanation.
- **security:** Treat the rehearsal as read-only and fail closed when a surface cannot be inspected. Never include credentials, cookies, or secret form values in the pendant summary. Clearly label inferred consequences versus observed consequences, attach source IDs and freshness, and require a new physical approval if the owner later commits after the plan expires.
- **missing:** A typed cross-surface shadow-execution contract that returns observed, inferred, and unknown effects without invoking executor actions; State-diff adapters for Mac actions and authenticated browser commands, including recipient/spend/irreversibility annotations; A durable plan snapshot with freshness expiry and a commit token bound to the exact snapshot; A compact owner-facing fork renderer on the dashboard and pendant that can say 'unknown' rather than inventing a consequence

### "“If the Mac, browser, relay, and pendant disagree about what happened, stop and tell me before doing anything else.”"
- **useful because:** A stale browser receipt, lost relay response, or missing pendant playback ACK can currently leave the system unsure whether an action happened. The owner needs a visible quarantine state: freeze dependent follow-ups, prevent duplicate submissions, identify the disagreement, and offer only read-only verification or explicit recovery. This protects against the most dangerous failure mode—confidently doing something twice.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic event reconciliation and idempotency checks; use the expensive model only to translate a confirmed discrepancy into one short explanation.
- **latency:** Detect conflicts as events arrive, ideally under 1 second; produce a verification card under 3 seconds. Recovery remains owner-confirmed.
- **cost:** Negligible model cost in the normal path; durable event indexing and cross-surface joins dominate.
- **security:** Quarantine records must contain opaque IDs and hashes, not page content or credentials. Fail closed on missing authentication or sequence gaps. Never infer success from timeout. Keep the quarantine durable across relay/Mac restarts and make release scope-specific, not a global override.
- **missing:** A shared event identity linking relay jobs, Mac jobs, browser commands, action receipts, and pendant delivery events; A durable conflict state machine with dependent-job suppression and scope-limited release; A read-only verifier that can ask each reachable surface for its authoritative status without replaying actions; Owner-visible evidence and provenance for why a job was quarantined

### "“Before you give me anything important, prove that you can hear me and that I can hear you.”"
- **useful because:** A successful server job is not evidence that the worn device can deliver intelligible audio. This capability runs a short, reversible end-to-end check: pendant microphone capture, USB/relay transport, Mac pipeline, 24 kHz downlink, bridge playback, and authenticated playback ACK. It reports the failing segment and refuses to present time-sensitive content as delivered when the path is degraded.
- **path:** pendant → relay → mac
- **model tier:** Deterministic hardware/network test vectors and measured counters; no model call except optional one-sentence owner explanation.
- **latency:** A basic loopback and ACK in under 3 seconds; extended codec/packet-loss test under 15 seconds. It must never interrupt an active conversation without confirmation.
- **cost:** Near-zero inference cost; a small generated test artifact and telemetry record are the main costs.
- **security:** Use synthetic tones or fixed test phrases, never retain owner speech. Mark test artifacts separately from real briefings, authenticate device sessions, and report only aggregate metrics aloud. Do not claim microphone privacy or successful playback from a server receipt alone.
- **missing:** A first-class diagnostic transaction that binds uplink evidence, downlink artifact, bridge metrics, and pendant ACK into one test ID; A device-side synthetic capture/playback mode that cannot accidentally upload or store owner audio; Threshold policy for declaring the path usable, degraded, or unsafe, with measured codec/packet-loss evidence; A preflight hook for urgent briefings that can defer delivery rather than silently queueing into a broken path


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities. The strongest is “Take me back to where I left off”: sw1’s existing offline bookmark becomes a source-linked Mac/browser context card and confirmed restore, using bounded context handoff rather than a new resume system. I also proposed delivery-truth for briefings (report only what was actually played; this is close to existing ACK/item primitives and should be treated as wiring, not a fourth queue) and a USB-local “move this conversation to my Mac” handoff that works today despite LTE being unregistered. I still need implementation of a USB serial handoff listener, a durable marker/context foreign-key, and a real relay/Mac/browser/device correlation ID. I also need the owner to choose restore confirmation behavior and disclosure boundaries; until then these must remain conservative, configurable, and review-first.

**Biggest unknown:** Whether the existing USB serial firmware path already has a safe extensible message type and authenticated session handshake. The earlier USB-tethered feasibility request is still unanswered, so I cannot honestly claim the local handoff is runnable yet.

