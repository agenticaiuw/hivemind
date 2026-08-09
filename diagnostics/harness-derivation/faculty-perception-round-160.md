# Harness derivation — faculty-perception — round 160

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser observability after TCC grant** — At 2026-08-08T02:40:59Z, /observe reports inputReachability.status=verified, Accessibility and Screen Recording trusted, secureInput=false, and uiActionsWillReachTheScreen=true for com.aipendant.agent. /ops/status reports browser extension online with Safari tab 1163292 at x.com, zero pending commands, relay reachable on D1, and no required permissions missing. No pendant appears in the live device inventory; only home-macbook-bridge is online.
  - evidence: Authenticated GET /observe, GET /ops/status, GET /browser/status; discover:devices returned Safari on MacIntel online, home-macbook-bridge online, cloudflare-contract-test offline.

## Capabilities it proposed

### "Before you act, tell me whether the situation is still the one I asked about: which Mac app and browser tab are foreground, whether the browser bridge and relay are live, whether permissions changed, and what would make the plan unsafe or stale."
- **useful because:** It prevents the most dangerous class of silent mistakes: a plan aimed at yesterday's tab, a different foreground app, or a disconnected relay being executed as though nothing changed. It is a cross-surface reality check no single node can establish.
- **path:** pendant → relay-realtime → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap deterministic perception first; escalate to realtime only to explain the resulting warning in speech. No background LLM is needed for the checks.
- **latency:** Under 500 ms when all surfaces respond; stale or missing sources must be reported explicitly rather than hidden behind a timeout.
- **cost:** Near-zero model cost; dominant cost is three authenticated local/relay reads and optional browser inspection.
- **security:** Return metadata and hashes, not page secrets or screenshots by default. A changed foreground app, tab identity, permission state, or relay device identity should downgrade confidence and require confirmation before irreversible actions.
- **missing:** A signed, single-snapshot contract joining /observe, /ops/status, /browser/status, and relay device state with one observedAt and per-source freshness.; A policy hook in faculty-judgement that turns identity/freshness drift into confirmation rather than merely displaying it.; Pendant-originated presence when the pendant eventually exists; today the answer must say no pendant is registered.

### "Show me exactly what you believe will change before you click, type, send, or delete—then verify the target is still the same immediately before execution."
- **useful because:** The system can now reach the screen (verified Accessibility, Screen Recording, and input posting), so it should turn perception into a concrete safety barrier: the owner sees the intended app, tab, target, and mutation, not a vague promise that an action is reversible.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic target extraction and diffing first; use the expensive realtime model only to summarize an ambiguous visual mismatch. Use a cheaper background model for drafting the preview.
- **latency:** Preview in 1 s; final preflight immediately before action in under 300 ms. Any mismatch pauses for owner confirmation.
- **cost:** Low: one browser inspection or local UI observation plus a structured diff. Vision inference is the dominant cost and should be skipped when DOM/AppleScript evidence is sufficient.
- **security:** Previews must redact secrets, message bodies, and passwords; never echo typed secret text. The final check must bind app bundle ID, tab/session ID, URL origin, target locator, and a content digest so a same-looking but different target cannot pass.
- **missing:** A first-class dry-run/precondition schema consumed by /execute and browser actions, rather than a prose preview.; A stable target digest from the Mac observation and browser inspection that survives only until the next mutation.; Owner confirmation semantics on the pendant for a changed target, including offline refusal when no relay is available.

### "When you answer me, tell me where the words actually went: Mac speaker, relay socket, bridge, or pendant speaker—and whether that endpoint confirmed playback, not merely that a job completed."
- **useful because:** Today a completed job or relay 'delivered' state can mean only that bytes were handed to a socket; the owner cannot know whether they heard the answer or whether the system silently fell back to the Mac. This would make spoken interaction honestly observable across every body.
- **path:** pendant → relay-realtime → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic event correlation and state derivation; no LLM is needed except a short realtime explanation when the route is ambiguous.
- **latency:** Attach route and confidence to the answer within 200 ms of the final playback event; if confirmation is absent, say 'unconfirmed' immediately rather than waiting indefinitely.
- **cost:** Negligible model cost. Engineering cost is a small event protocol and bounded local queue; network and flash writes dominate, so retain only compact sequence/checksum metadata.
- **security:** Device events must be authenticated as device-originated, scoped to the job/artifact, monotonic, and replay-resistant. Never treat an admin HTTP acknowledgement or Mac-side completion as hearing. Audio content need not leave the endpoint.
- **missing:** A route-identity field on each speech artifact and a device-originated playback event carrying artifact ID, sequence/checksum, start, finish, and interruption reason.; Firmware emission and retry of that event over the accepted bounded NVS queue; the pendant is currently absent from the registry, so this cannot be verified live yet.; Relay and Mac readers that refuse to derive 'heard' from job completion and surface unconfirmed delivery to the owner.

### "Let me ask, “Why do you believe that?” and get a replayable evidence trail: the exact observations, timestamps, source identities, transformations, uncertainty changes, and decision handoffs that led to your answer or action—without exposing private page or audio content unless I request it."
- **useful because:** Today the system can act across the pendant, relay, Mac, and authenticated browser, but the owner cannot independently reconstruct how a cross-surface belief was formed. A compact causal replay would turn unexplained automation into something inspectable, correctable, and trustworthy—especially when one surface was stale, unavailable, or contradicting another.
- **path:** pendant → relay-realtime → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic append-only event linking and hash verification; use a cheaper model only to summarize the trace. The realtime model should never be required to reconstruct facts.
- **latency:** Add under 20 ms per recorded observation and under 1 s to render a bounded replay. The owner can request a deeper trace asynchronously.
- **cost:** Low inference cost. Storage and hashing dominate; retain redacted metadata and content hashes by default, with bodies/audio held only under the owner's explicit retention policy.
- **security:** The trace itself can reveal sensitive URLs, app names, timing, and inferred intent. Encrypt at rest, redact secrets before hashing, separate owner-visible summaries from privileged raw evidence, and make deletion/revocation propagate across relay, Mac, browser, and pendant caches. A hash proves consistency, not truth; show source and uncertainty rather than implying cryptographic certainty.
- **missing:** A cross-surface correlation envelope with traceId, parent observation IDs, source identity, observedAt, freshness, transformation name/version, and uncertainty disposition.; Relay-to-Mac and browser-to-relay event transport that preserves those links instead of returning ephemeral tool text.; A bounded encrypted event ledger with revocation and export, plus dashboard views for contradiction, stale evidence, and missing links.; A faculty-judgement contract requiring every consequential decision to cite its evidence IDs and every faculty-action result to append an outcome or unknown event.

### "Warn me when your surfaces disagree about reality—such as the Mac saying a browser is online while the relay says it is stale, or a page changing between what the browser read and what is on screen—and tell me which source you will trust and why."
- **useful because:** A confident answer assembled from contradictory observations is more dangerous than an explicit pause. The owner should receive a visible contradiction, not a silently selected source, before an action or spoken claim turns stale state into fact.
- **path:** pendant → relay-realtime → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic temporal and identity comparison; a small model may phrase the warning, but source ranking and contradiction detection must be rules-based.
- **latency:** Detect contradictions during evidence collection, before planning completes; warning generation under 300 ms, with no action dispatched until the conflict is resolved or explicitly accepted.
- **cost:** Negligible model cost; dominant cost is parallel observations and retaining compact source fingerprints.
- **security:** Do not reveal hidden account state merely because two sources disagree. Apply per-source permissions, redact sensitive values, and distinguish unavailable from negative. An owner override must be scoped to one trace and expire after the relevant state changes.
- **missing:** A common identity and clock model for Mac, browser, relay, and eventual pendant observations.; Explicit source precedence and contradiction classes (stale, identity mismatch, content mismatch, permission mismatch, unreachable).; A judgement/action gate that treats unresolved contradiction as a stop condition, with a pendant confirmation path when connected.

### "Let me set different proof rules for different things—for example, draft from a browser read, but never send a message without a live screen match; accept a calendar read from the Mac, but require wearable confirmation before treating a spoken alert as heard."
- **useful because:** The system currently has one broad notion of success despite radically different risks. Owner-defined evidence thresholds would let it be fast for low-risk information and deliberately demanding for communication, deletion, purchases, or claims that the owner heard something.
- **path:** pendant → relay-realtime → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Policy evaluation should be deterministic and local to the judgement/action boundary; use a cheaper model only to map natural-language preferences into a typed policy, with confirmation before activation.
- **latency:** Evaluate in milliseconds on every proposed action. Policy editing can take seconds and should produce a human-readable test case before it becomes active.
- **cost:** Minimal inference cost after policy compilation; storage is a small signed policy document replicated to relay and Mac.
- **security:** Policies must be scoped by action, source, account, and risk—not broad blanket permissions. Prevent prompt or web content from changing them. Require owner confirmation for policies that weaken proof requirements, and keep an immutable audit of policy changes.
- **missing:** A typed evidence-policy language covering required sources, freshness bounds, identity binding, contradiction handling, and owner confirmation.; A shared policy evaluator used by relay judgement, Mac planner, browser actions, and pendant delivery—not separate local heuristics.; A safe natural-language policy editor with simulation against past traces so the owner can see false accepts and false stops before enabling a rule.


## Changes it proposed to its own stack

### `integration` — Expose the already-live GET /ops/snapshot as the implementation behind read_continuity_snapshot, preserving include filters, since bound, maxItems, and per-source freshness/unknown states. The granted tool currently fails resolution (best match 0.447) even though /ops/snapshot returns the needed authenticated state.
- **owner gets:** The owner gets one truthful answer to “what is live and what happened while I was away?” instead of a tool error or a model inferring across multiple unaligned endpoints.
- effort: Small adapter plus schema registration and contract tests against /ops/snapshot and /pipeline; no new storage required.  ·  risk: A naive adapter could overstate freshness or convert absent pendant data into false offline claims. Preserve source timestamps, mark pendant unknown/not registered, and cap the response. Recovery is to fall back to direct endpoint reads.
- cost: Negligible API cost; one local authenticated request. No hardware cost.  ·  latency: Adds one local request, typically sub-second; parallelize source reads if the route later fans out.
- security: Keep bearer authentication and redact URLs, claims, and audio metadata according to existing route policy; do not expose the relay admin key or page contents.
- depends on: The existing GET /ops/snapshot route; The existing GET /pipeline route; A resolver manifest entry whose name and enum schema exactly match read_continuity_snapshot


## What it asked for

_Nothing._
