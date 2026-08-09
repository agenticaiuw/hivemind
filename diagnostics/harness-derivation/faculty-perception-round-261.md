# Harness derivation — faculty-perception — round 261

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live cross-surface status 2026-08-09 round 261** — The Mac local agent is healthy and relay-reachable; Accessibility and Screen Recording are now granted and required permissions.ready=true. Browser extension is online with one Safari tab at youtube.com/watch (tab 85). Device discovery shows nrf9160-pendant offline (last seen 2026-08-09T02:56:31.366Z), home-macbook-bridge online, and mesh-tools-probe-a/b online. GET /v1/devices/status is not a route on the Mac local agent, so the local 404 must not be interpreted as relay registry absence.
  - evidence: GET /ops/status HTTP 200 and discover(category=devices) live results; probe GET /v1/devices/status returned local-agent 404 with hint to /capabilities.

## Capabilities it proposed

### ""Tell me what is actually true right now, and point out anything contradictory or stale.""
- **useful because:** The live system now has an offline nrf9160-pendant, an online Mac bridge, an online Safari extension, and online probe devices; a single 'online/offline' answer can be structurally misleading. This would give the owner a perception-grade truth report with per-surface timestamps, source authority, contradictions, and explicit unknowns instead of silently merging incompatible states.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** cheap background model for normalization and contradiction labeling; realtime only when the owner asks verbally
- **latency:** under 2 seconds for a bounded snapshot; under 5 seconds if browser and relay checks are refreshed
- **cost:** low: one bounded relay/Mac snapshot and deterministic comparison; model cost only for natural-language rendering
- **security:** Read-only. Do not expose tokens, page contents, or credentials. Mark the pendant registry as stale/offline and distinguish registry evidence from Mac-authored fleet claims.
- **missing:** one authenticated cross-surface endpoint that includes pendant registry, Mac status, browser status, relay freshness, and pipeline freshness with source timestamps; a contradiction policy defining authority and stale thresholds per field; a durable snapshot ID so a spoken answer can be audited later

### ""My pendant is offline—keep me informed through whatever is still available, then catch me up when it reconnects.""
- **useful because:** The owner should not lose urgent results merely because the worn node is absent. Today the Mac bridge and browser are online while nrf9160-pendant is offline; this capability turns that real asymmetry into graceful service: route low-risk notices to the Mac/browser, preserve their provenance, and reconcile only undelivered items when the pendant returns.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** background model for prioritization and deduplication; deterministic routing for urgent/safe notices; realtime only for an active voice turn
- **latency:** notice fallback within 3 seconds; reconnect reconciliation within 10 seconds of a verified pendant heartbeat
- **cost:** low-to-medium: relay storage and Mac/browser delivery calls dominate; model calls can be avoided for already-classified events
- **security:** Require confirmation before sending sensitive content to desktop/browser surfaces. Never claim the owner heard an item. Use opaque item IDs and retain only bounded summaries until a device playback event is received.
- **missing:** a relay policy engine that selects a fallback surface based on sensitivity and urgency; Mac/browser notification delivery with an owner-visible acknowledgement distinct from pendant playback; a real pendant heartbeat and played/consumed event (the accepted audio_delivery_ack_queue is needed when hardware is online)

### ""Did that action really happen, what changed, and what still needs me?""
- **useful because:** A Mac job can be marked complete while browser state, relay delivery, or the owner's physical hearing remains unknown. This capability would join the planned action, execution receipt, browser result, post-state observation, and device/relay freshness into a single evidence ladder: executed, externally verified, owner-visible, or unresolved—with the next safe recovery step.
- **path:** mac → browser → relay → pendant → dashboard
- **model tier:** cheap model for summarizing evidence; deterministic state comparison and confidence gates before any recovery action
- **latency:** 3–8 seconds after an action, with a fast preliminary status immediately
- **cost:** low: primarily existing receipts and read endpoints; occasional vision/browser verification is the dominant cost
- **security:** Read-only verification by default. Do not replay or undo automatically. Redact secrets from browser snapshots and make any recovery action confirmation-gated.
- **missing:** a common receipt schema joining jobId, commandId, ledger step, browser result, pipeline run, and device event; postcondition probes for key Mac/browser actions; a status vocabulary that separates execution, external verification, visibility, and owner-heard evidence

### ""What was I looking at when I said that, and what did I mean by ‘this’ or ‘that’?""
- **useful because:** Voice references routinely depend on the owner's live screen or browser context. The owner cannot currently recover the referent because pendant audio, Mac active-app state, browser tab state, and relay transcripts have no shared temporal anchor. This would answer deictic questions with a bounded, provenance-labeled reconstruction instead of guessing.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** cheap model for referent ranking after deterministic time-window joins; realtime only during the active utterance if clarification is needed
- **latency:** under 2 seconds for recent context; under 8 seconds for a historical reconstruction
- **cost:** low-to-medium: storage and screen/browser capture dominate; model cost is limited to ranking candidate referents
- **security:** Capture only around an utterance window, redact secrets, encrypt anchors, and require explicit owner opt-in for screen context. Never upload raw screen/audio to the relay by default.
- **missing:** a shared monotonic/UTC correlation envelope across pendant audio, relay turns, Mac active-app observations, and browser tab snapshots; an owner-visible referent record with source, timestamp, confidence, and expiry; a local redaction and retention policy for screen/audio context

### ""Put this aside so I can get back to exactly where I was later.""
- **useful because:** A true interruption bookmark should preserve the owner's spoken intent, the active browser page and scroll/selection, the Mac application/document state, and the relay conversation position as one recoverable object. Today those surfaces can each be inspected, but there is no cross-node, owner-addressable moment that can be restored later.
- **path:** pendant → mac → browser → relay → dashboard
- **model tier:** background model to summarize the bookmark and infer a title; deterministic capture and restore; realtime is unnecessary
- **latency:** capture under 3 seconds; restore under 10 seconds with confirmation before opening or modifying anything
- **cost:** medium: local encrypted state and optional browser/page capture dominate; summary generation is small
- **security:** Keep the bookmark local by default, redact credentials and private page content, expire it automatically, and require confirmation before restoring tabs, files, or app state.
- **missing:** a cross-surface bookmark schema with atomic capture and a resumable restore plan; browser support for scroll position, selection, and session restoration; Mac app adapters that can snapshot and restore document context without destructive writes; a pendant command or button gesture to create and retrieve bookmarks offline

### ""Make sure interruptions reach me at the right moment, not merely as soon as they are generated.""
- **useful because:** The collective currently knows whether nodes are online, but not whether the owner is speaking, watching a video, typing, driving attention elsewhere, or able to hear. This capability would arbitrate attention across pendant, Mac audio, and browser: hold low-priority notices, deliver urgent ones through the least disruptive live surface, and explain why something was delayed.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** deterministic policy and local signals first; cheap model only to classify ambiguous notice urgency; realtime reserved for an active conversation
- **latency:** urgent safety notice under 1 second; ordinary notices evaluated every few seconds; deferred items reconciled on focus change
- **cost:** low-to-medium: continuous lightweight local signals and bounded queue metadata; little model usage
- **security:** Attention sensing must remain local unless explicitly shared. Sensitive notices require a trusted surface and confirmation. Never infer availability solely from a stale online flag.
- **missing:** a local attention-state stream from pendant audio/VAD, Mac active app/audio output, and browser playback/focus; a relay-wide priority and deferral policy with expiry and escalation rules; delivery receipts that distinguish presented, dismissed, deferred, and physically heard


## Changes it proposed to its own stack

### `model-routing` — Add an evidence-fence router: before any model is allowed to say an action completed, it must classify the claim as observed, inferred, stale, or unknown from independent source records. High-impact actions require a second-source postcondition; absence of a pendant playback event can never be upgraded by Mac completion. Route only unresolved contradictions to the expensive realtime model, while deterministic evidence joins handle ordinary receipts.
- **owner gets:** The owner stops hearing confident lies such as 'done' when only a local process finished. They get a short answer that says exactly what happened, what was independently verified, and what remains unknown.
- effort: Medium: define claim states and source precedence, then gate completion language in relay/Mac planners and dashboard rendering.  ·  risk: Some answers become explicitly unresolved and may feel less convenient; recover by offering a read-only verification or a confirmation-gated retry. Incorrect source precedence could suppress useful answers, so retain raw evidence links.
- cost: Reduces expensive model calls by handling routine evidence deterministically; small storage overhead for claim metadata.  ·  latency: Adds sub-second local classification; only contradictions invoke the expensive model.
- security: Improves security by preventing ungrounded claims and keeping secrets out of model summaries; does not grant new write authority.
- depends on: A common receipt schema joining jobs, browser results, pipeline runs, and device events; The accepted audio_delivery_ack_queue when a pendant is online; Postcondition probes for important Mac/browser actions

### `context` — Create a local-first temporal correlation fabric that assigns every utterance, browser observation, active-app observation, relay turn, and device health frame a shared correlation envelope with monotonic sequence, wall-clock estimate, source, freshness, and redaction status. Expose it as a user-facing timeline and use it to build referent recovery, interruption bookmarks, and attention decisions; do not treat endpoint timestamps as interchangeable without uncertainty bounds.
- **owner gets:** The owner can ask about a moment in their life and get the actual surrounding context—or recover an interrupted task—rather than a plausible story assembled from unrelated timestamps.
- effort: Large: protocol changes across firmware, relay, Mac, and browser; local encrypted storage, clock uncertainty handling, and UI are required.  ·  risk: Incorrect clock alignment could create convincing but false associations. Recover by showing source timestamps and uncertainty, keeping raw events available locally, and refusing joins outside the bound.
- cost: Moderate local storage; low inference cost after indexing. No continuous cloud model requirement.  ·  latency: Negligible capture overhead; historical joins become near-instant after indexing.
- security: Improves privacy by making correlation local-first and redaction-aware, but creates a sensitive activity timeline requiring encryption, expiry, and explicit export controls.
- depends on: Pendant monotonic health/audio sequence frames; Mac active-app and screen observation events; Browser tab/selection/scroll observation events; Relay turn identifiers and delivery records; A clock uncertainty and retention policy


## What it asked for

_Nothing._
