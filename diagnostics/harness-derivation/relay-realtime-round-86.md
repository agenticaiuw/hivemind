# Harness derivation — relay-realtime — round 86

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before you act, show me the exact changes you plan to make across my Mac and logged-in browser, with evidence, then let me approve."
- **useful because:** This gives the owner confidence when multiple surfaces are involved. It’s especially valuable for private accounts: they can review a sourced plan without risking accidental submission.
- **path:** pendant → relay → browser → mac-bridge → relay
- **model tier:** Use relay for quick narration; use mac-planner and browser harness to assemble a typed plan with citations; mac-vision only if GUI extraction is required.
- **latency:** A few seconds for a verbal summary; longer for assembling evidence and extracting fields. Approval step is interactive and must be fast.
- **cost:** The cost is dominated by authenticated page reads and extraction across multiple tabs/sessions. Relay narration is cheap.
- **security:** Handle sensitive content carefully: store only hashes/snippets necessary for provenance, avoid logging full page contents, and ensure approval is required before irreversible actions.
- **missing:** A typed cross-surface change plan format with provenance and before/after diffs; Reliable browser session affinity and typed results (some pieces exist, defect still open); A relay-visible review queue with TTL and partial-failure handling; Durable storage for evidence bundles

### "When I say “send that to Alex” or “open the thing we were looking at,” resolve “that/thing” across my recent pendant conversation, Mac workspace, and authenticated browser tabs, tell me exactly what you found, and carry out the request without making me repeat the context."
- **useful because:** People naturally use deictic references while moving between devices. Today the relay has conversation context, the Mac has apps/files, and the browser has sessions, but no shared, durable referent identity; the owner must restate names, URLs, or files and can easily send the wrong artifact.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay performs cheap reference extraction and asks a short clarification only when candidates conflict; a slower background model builds and ranks the cross-surface artifact graph; mac-planner/mac-vision and browser-extension verify and execute the selected action.
- **latency:** A spoken candidate brief in under 2 seconds from cached metadata; up to 5 seconds for fresh Mac/browser evidence. Execution may continue asynchronously, with a concise spoken receipt and dashboard detail.
- **cost:** Roughly $0.01–$0.05 per invocation depending on whether fresh Mac/browser inspection and background disambiguation are needed; most cost is evidence extraction and the final action plan, not the short relay response.
- **security:** The graph must retain provenance, sensitivity labels, and short TTLs rather than raw page contents by default. Never silently choose between materially different recipients or documents; speak the candidates and chosen target before an irreversible send. Browser credentials stay in the extension and Mac data stays local; relay receives identifiers, excerpts, and receipts.
- **missing:** A durable cross-surface artifact/reference graph linking transcript spans, pendant sessions, Mac windows/files, browser tabs, and action receipts; A resolver protocol that returns ranked candidates with provenance and confidence to the realtime relay; Entity-aware plan/execute support for references (recipient, attachment, URL, message) rather than only literal goals; Retention, redaction, TTL, and deletion controls exposed in the dashboard; A resumable job that can wait for an offline Mac/browser and report partial resolution without losing the spoken context


## Changes it proposed to its own stack

### `relay` — Implement the granted intent-routing and job-status schemas as real relay features: a typed intent envelope emitted from speech recognition, routed to mac-planner/mac-vision, with durable job records and partial-failure handling. Include a small relay-visible capability inventory endpoint so the relay can discover its own routes/tools, plus backoff and offline handling for browser-extension heartbeat and queued commands.
- **owner gets:** The owner can say something once and trust it will be routed correctly, keep running after they stop talking, and later ask what happened and get a precise answer. This reduces confusion and avoids repeating requests while walking away.
- effort: Medium-high: new relay endpoints, durable storage for job records, integration with existing plan/execute paths, and test harness updates for offline/partial-failure scenarios.  ·  risk: Misrouting or duplicate execution. Mitigate with idempotency keys, explicit intent labels, and job state transitions. Provide receipts and undo where already supported.
- cost: Adds relay storage and a bit more per-request processing; dominated by downstream Mac/browser work rather than relay compute.  ·  latency: Slight overhead to wrap and record intents, but faster perceived UX because status is queryable without waking the Mac.
- security: The relay becomes a more sensitive control plane. Require authentication for intent submission, sign job records, and redact sensitive context in logs.
- depends on: A durable job runner or equivalent relay-side persistence for job records; A relay capability inventory endpoint (or route) to avoid blind routing

### `integration` — Add a cross-surface semantic clipboard and reference resolver: every eligible spoken noun phrase, Mac window/file, browser tab/form, and execution receipt gets a short-lived opaque artifact ID with provenance. Expose a resolver endpoint that can return ranked candidates and a compact evidence card, then let plan/execute consume an artifact ID plus an explicit operation (share, attach, open, summarize, send). The relay should retain only the ID and evidence card; local bridges retain the underlying content.
- **owner gets:** The owner can say “send that,” “use the PDF from earlier,” or “open the page I was looking at” while away from the desk and have the system use the right item instead of forcing repetitive, error-prone explanations.
- effort: Medium-high: shared schema and TTL store, adapters in pipeline/session, Mac and browser bridges, resolver tests for ambiguity, and dashboard inspection/deletion UI.  ·  risk: A stale or wrongly ranked reference could affect the wrong artifact. Mitigate with provenance, freshness display, confidence thresholds, candidate disambiguation for conflicts, and receipts that include the resolved artifact. Recover by invalidating IDs and replaying against fresh state.
- cost: Small storage and metadata overhead; approximately one extra cheap resolver/model call for ambiguous references, with no extra cost for clear cached IDs.  ·  latency: Usually tens to hundreds of milliseconds from metadata; fresh inspection adds normal Mac/browser round-trip latency.
- security: Improves containment by keeping raw content on its owning surface, but IDs must be unguessable and access-scoped. Apply per-surface ACLs, sensitivity labels, encryption, TTL, and explicit deletion.
- depends on: A durable resumable job/receipt mechanism for offline Mac or browser surfaces; A shared artifact-ID and provenance schema across /pipeline/audio, sessions, Mac planner, and browser extension; Resolver-aware extensions to POST /plan and POST /execute; Dashboard controls for reference history and revocation

### `hardware` — Add a low-power coin vibration motor and a second capacitive/tactile input zone (or a distinct double-click-capable button) to the pendant, with firmware events for tap, double-tap, hold, and candidate-next. Use it as a private confirmation/disambiguation channel for cross-surface references: the relay speaks a candidate summary, a short vibration marks the default, and the owner taps to cycle or holds to accept/cancel.
- **owner gets:** The owner can safely resolve “that one” or stop an accidental action while walking, driving, or in a noisy place without relying on a screen or saying sensitive document names aloud. It also makes the pendant useful when audio playback is masked or speech recognition is unreliable.
- effort: Medium hardware revision plus firmware event protocol, battery characterization, enclosure redesign, and relay support for a small finite-state interaction. Keep the existing button/LED behavior as a fallback for old pendants.  ·  risk: Added power draw, false taps, and confusing vibration patterns could annoy the owner or drain the battery. Use short bounded pulses, debounce and explicit timeouts, provide an LED-only fallback, and make every accepted action produce an audio receipt. Existing units remain compatible without this interaction.
- cost: Approximately $1–$4 in components and modest assembly/enclosure cost; roughly 5–20 mA only during brief vibration pulses, with near-zero idle draw. No meaningful per-invocation API cost.  ·  latency: Adds under 100 ms locally for input recognition; avoids waiting for a spoken repeat, reducing end-to-end disambiguation time in noisy conditions.
- security: A physical accept/cancel gesture provides stronger local presence evidence, but it must not become an irreversible gate for ordinary reversible actions. Do not encode document contents in vibration patterns; keep payloads opaque and use encrypted device-to-relay transport.
- depends on: The cross-surface artifact-ID/reference resolver and ranked candidate evidence cards; Firmware event schema and relay support for tap/double-tap/hold plus vibration commands; A durable action receipt so the owner can recover if the link drops mid-gesture


## What it asked for

_Nothing._
## Its own summary

Recorded three concrete additions: (1) a cross-surface semantic reference capability so “send that” resolves to a provenance-backed Mac/browser/conversation artifact; (2) the integration layer required to make opaque artifact IDs, ranked evidence, TTLs, and resolver-aware plans/execution real; and (3) a pendant hardware/firmware enhancement with vibration plus richer tap gestures for private, reliable disambiguation and cancellation. These address a capability the owner cannot have today without repeating context or using a screen.

**Biggest unknown:** The exact pendant enclosure, battery budget, and available GPIO/input options for adding haptics and a second gesture input; the software proposals can begin with existing hardware, but the physical interaction needs that specification before being engineered.

