# Harness derivation — faculty-perception — round 229

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live system status round 229** — Live GET /ops/snapshot reports Mac agent v0.5.0 online, browser extension online on Safari with 5 tabs (active USPS Tracking), Accessibility and Screen Recording both granted, all listed automation permissions ready, relay reachable with D1 and Mac bridge online. No pendant is present in discover devices; only home-macbook-bridge is online plus offline contract-test mobile.
  - evidence: read_continuity_snapshot(include=['relay','pipeline']) invoked GET /ops/snapshot at HTTP 200; discover(devices) returned Safari on MacIntel online, home-macbook-bridge online, cloudflare-contract-test offline.

## Capabilities it proposed

### "Before you do anything consequential, tell me whether the evidence is fresh and sufficient: what I said, what the browser showed, what the Mac changed, and whether the pendant actually confirmed hearing it."
- **useful because:** This would make the hive trustworthy instead of merely capable. Judgement would receive a signed, time-indexed evidence packet and refuse to treat a stale browser page, a relay socket write, or a Mac-side completion as reality. It combines the wearable's capture-quality verdict, relay job identity, Mac receipt, browser capsule hash, and (when a pendant exists) playback acknowledgement into one explicit known/unknown gate.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the cheap deterministic perception/validation path for freshness, hashes, sequence numbers, and quorum; invoke realtime only to explain the resulting verdict to the owner. No model is needed to decide whether an acknowledgement or hash exists.
- **latency:** Under 300 ms when all evidence is local; up to 2 s while waiting for a relay/browser receipt. If a required source is stale, return 'unknown' immediately rather than waiting indefinitely.
- **cost:** Near-zero model cost; mostly authenticated reads and hash comparisons. A realtime explanation is a few hundred tokens only when the owner asks.
- **security:** Evidence packets must contain capsule IDs and redacted hashes, not page bodies or secrets. Consequential execution must require an explicit freshness/quorum policy; never infer owner-heard from relay delivered or Mac completed. Missing: a relay-to-Mac capsule transport and the already-accepted pendant playback ledger when hardware is connected.
- **missing:** relay endpoint returning stable browser-read ID and content hash; Mac ingestion of relay evidence into the existing evidenceCapsules/browserProvenance stores; judgement/action policy that consumes a freshness-and-quorum packet; live pendant connection for device-originated capture/playback evidence

### "Tell me when the system is believing two incompatible things about me or the world, show both observations and their provenance, and stop the weaker one from steering an action until I resolve it."
- **useful because:** The current memory projection can repeatedly inject a machine-originated America/Chicago preference despite the Mac actually being America/New_York. A contradiction sentinel would catch this class of failure before it changes a reminder, message, purchase, or browser action. It is perception, not judgement: it reports the conflict, authority, freshness, and blast radius while leaving the owner in control.
- **path:** relay → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Deterministic normalization and provenance rules first (timestamps, timezone, URL identity, device last-seen, capsule hashes); use a cheap background model only for extracting candidate claims from unstructured text. Realtime is reserved for speaking a concise warning.
- **latency:** Continuous checks after memory/context refresh and before action planning; under 500 ms for structured claims, under 5 s for text extraction. Never block ordinary conversation on a low-confidence text contradiction.
- **cost:** Low: hash/normalization work and occasional background extraction. No realtime call unless an owner-facing warning is requested.
- **security:** Do not expose private page text in the warning; show source class, host, timestamp, and redacted claim. Never silently delete or rewrite an owner fact. Missing: a durable conflict record, provenance-aware context projection hook, and a judgement policy for which conflicts are blocking versus advisory.
- **missing:** conflict-record store with first-seen/last-seen and resolved-by-owner fields; context projection hook that labels or withholds contradictory machine facts; normalizers for timezone, calendar, browser page, and device liveness claims; cross-surface reader for relay and browser evidence

### "Warn me, before any private page, microphone segment, or screen observation leaves my devices, exactly what would leave, where it would go, and let me allow only the redacted parts."
- **useful because:** The browser, wearable, Mac vision loop, and cloud relay each see different pieces of sensitive context. Today `untrusted:true` is only prompt framing, and relay browser reads have no durable provenance. A boundary inspector would make privacy observable at the moment it matters: classify login walls and secret fields, attach a redaction manifest and destination, and prevent a cloud call when the owner has not allowed that class.
- **path:** pendant → mac-vision → browser-extension → relay → dashboard
- **model tier:** Use local deterministic classifiers and existing browser secret-locator/redaction rules for the first pass; use a local vision model only for ambiguous screen regions. Realtime should explain or ask permission, never perform classification that can be done locally.
- **latency:** Under 150 ms for browser DOM fields and microphone metadata; under 1 s for a screen-region scan. A blocked cloud request must fail closed within the same turn.
- **cost:** Near-zero API cost for metadata and DOM redaction; local vision cost is bounded by changed-screen regions. Cloud model cost is avoided when content is blocked or redacted.
- **security:** The inspector itself must not upload the secret it is trying to protect. Keep raw audio/screen local, expose only classifications, destination, byte counts, and hashes. Require confirmation for new destinations or unredactable sensitive content. Missing: relay enforcement of a redaction manifest, mounted browser provenance routes, and a local preflight hook in every cloud-bound path.
- **missing:** single preflight middleware covering realtime voice, relay browser reads, research, and vision uploads; relay contract accepting and enforcing redaction manifests/content hashes; mount browserProvenance routes and connect them to existing evidence capsules; owner policy for allowed sensitivity classes and destinations

### "When I say “that,” “this page,” or “the thing we just saw,” resolve the reference across my spoken turn, the active Safari tab, the Mac window, and the last browser or pendant event—and show me the exact object before acting."
- **useful because:** Deictic references are where a wearable mind quietly acts on the wrong thing. This would make the owner able to point conversationally at a real object while moving between pendant, Mac, and browser, without repeating URLs or titles. It is not a generic browser command: it is a time-bounded cross-surface referent with an explicit candidate and confidence, expiring when the tab or turn changes.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic recency/session joins first; use a cheap text model only to resolve pronouns against the bounded candidate list. Realtime handles the short clarification question, not the object lookup.
- **latency:** Candidate resolution under 250 ms; if ambiguous, ask one spoken clarification within 1 s and do not execute.
- **cost:** Usually zero additional model calls; ambiguous turns cost a small clarification completion. Storage is a bounded ring of opaque event references, not page bodies.
- **security:** Never send raw page contents to the relay merely to resolve “that”; send opaque capsule IDs, titles, hosts, and redacted snippets. Require confirmation when candidates differ in account, recipient, or destructive consequence. Missing: a shared temporal referent protocol, relay correlation IDs for browser reads, and a pendant event stream when the device is connected.
- **missing:** cross-surface referent protocol with monotonic event sequence and expiry; browser and Mac adapters that publish active-object references rather than only screenshots or text; relay session state that joins the spoken turn to those references; pendant-originated event sequence when hardware is available

### "Only interrupt me when the message is both urgent and likely hearable: combine my calendar or active meeting, Mac audio state, browser focus, and the pendant’s local noise/capture quality; otherwise hold it and tell me exactly why later."
- **useful because:** A notification that is delivered to a socket but masked by a meeting, muted Mac, or noisy street is functionally lost. This gives the owner an interruption policy based on actual conditions rather than a blind queue: urgency, social context, and acoustic reach are evaluated together, with a later explanation for every deferral.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic policy and live telemetry decide urgency, focus, volume, and acoustic quality. Use a cheaper background model to classify message urgency only when the sender or routine did not provide it; realtime speaks only a short alert or deferral explanation.
- **latency:** Evaluate within 200 ms of a candidate notification. If telemetry is stale, defer rather than claim it was heard; reassess on each heartbeat or focus change.
- **cost:** Near-zero for telemetry and rules; occasional small classification call per unlabelled notification. It reduces wasted TTS and repeat alerts.
- **security:** Calendar titles, browser URLs, and microphone metrics must remain minimized and redacted in the decision record. Never infer that a deferred alert was heard. Missing: a policy engine consuming cross-surface conditions, a pendant acoustic telemetry stream, and a durable per-notification reason ledger.
- **missing:** notification decision record with urgency, reachability, decision, and reason; Mac adapters for meeting/focus/volume and browser focus changes; pendant noise/hearability heartbeat when hardware is connected; relay scheduler hook that re-evaluates deferred alerts without duplicating them

### "Give me a physical panic button: one deliberate long-press on the pendant must freeze new cloud, Mac, and browser actions, cancel anything still cancellable, and leave me a local receipt of what was stopped and what could not be stopped."
- **useful because:** A wearable is the one surface the owner can reach while walking away from the Mac or when an automation starts doing the wrong thing. Today cancellation is scattered across jobs and browser commands and may require the Mac connection; there is no cross-surface emergency stop with a defined boundary. This would provide a real, immediate safety control rather than a conversational request that itself could be delayed or misheard.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** No model: firmware debounce/long-press, authenticated relay state transition, and deterministic cancellation. A cheap text model may summarize the receipt later; realtime is not on the safety path.
- **latency:** Pendant enters local freeze in under 100 ms; relay broadcasts the freeze in under 500 ms; Mac/browser acknowledge or report unreachable within 2 s. The freeze must work offline and survive reconnect until explicitly cleared.
- **cost:** Negligible runtime/API cost. Requires a firmware button handler, a bounded persistent local flag, relay freeze state, and cancellation fan-out.
- **security:** Protect against accidental presses with a long-press and haptic/audio confirmation, but do not make clearing the freeze easy for an attacker. Use device-scoped credentials, monotonic sequence numbers, and fail-closed behavior when the relay is unreachable. Missing: authenticated pendant control channel, relay global freeze primitive, Mac/browser cancellation fan-out, and firmware NVS state.
- **missing:** offline pendant freeze latch with long-press debounce and persistent sequence; relay per-owner emergency-stop state and push/broadcast path; Mac agent hook that cancels jobs and prevents new execute/plan dispatch; browser extension hook that cancels pending commands and blocks new polls; dashboard and spoken receipt distinguishing stopped, completed, and unreachable


## What it asked for

_Nothing._
## Its own summary

Round 229 established that the Mac is fully permission-ready (Accessibility, Screen Recording, and automation all granted), the Safari bridge is online with five tabs and USPS Tracking frontmost, the relay is reachable on D1, and no pendant is registered. I recorded that live fact and submitted three new capabilities: an evidence-gated action packet, a contradiction sentinel for provenance/freshness conflicts, and a privacy-boundary preflight (the last is adjacent to an earlier privacy proposal, so it should be treated as a warning rather than a wholly distinct idea).

**Biggest unknown:** There is still no live pendant-originated observation: no physical nRF9160 is registered, so capture quality, offline beacon, and playback cannot be verified end-to-end. The largest software gaps are the relay-to-Mac browser capsule bridge, a cross-surface causal/evidence gate, a mounted provenance/conflict store, and a single fail-closed privacy preflight on every cloud-bound path.

