# Harness derivation — faculty-judgement — round 238

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me my morning brief only when it is trustworthy; if anything is missing or duplicated, tell me that instead of pretending the day is clear.”"
- **useful because:** The current scheduled routines contain duplicate 07:00 briefs, and calendar/EventKit denial can look exactly like an empty calendar. This would make the first thing the owner hears each day honest: reconcile permissions, timezone, duplicate schedules, source freshness, and actual audio delivery before speaking content.
- **path:** relay → mac → browser → pendant
- **model tier:** Use deterministic reconciliation and policy evaluation first; reserve the realtime model for a one-sentence explanation only when conflicts need interpretation. Use the Mac for calendar/mail/routine reads, relay for durable run identity and attention arbitration, browser only when a brief includes authenticated page-watch evidence, and pendant ACKs for delivered/played truth.
- **latency:** Under 3 seconds for the preflight and reconciliation; up to 8 seconds only if a fresh mail/browser read is required. Never wait silently for a source: speak a short unavailable/duplicated status and queue the full brief.
- **cost:** Usually <$0.01 per run; dominated by one model explanation or fresh browser/mail read, not the deterministic checks.
- **security:** Do not speak calendar or mail contents if permissions are unknown or the owner is not in an allowed speaking context. Return provenance and the exact failed source. A duplicate routine must be proposed for disablement, never auto-deleted. Require owner confirmation before changing schedules.
- **missing:** A durable brief-run record joining routine ID, reconciliation result, generated artifact, and pendant delivery ACK; A scheduler hook that invokes reconciliation before each routine brief; A correction to notification/day-plan empty-source handling so unauthorised EventKit cannot become 'clear'; An owner-set policy for whether a degraded brief may contain partial content

### "“Read the page I mean, not whichever tab your stale session happens to return; if you cannot prove the target, stop and ask me.”"
- **useful because:** A live probe demonstrated that requesting tab 5696555 returned YouTube content from tab 3186198. A wrong-tab read can leak unrelated authenticated content or cause an action in the wrong account. This gives the owner a visible, fail-closed browser companion instead of silent misexecution.
- **path:** pendant → browser → mac → relay
- **model tier:** Deterministic tab identity and provenance checks do the work; use the realtime model only to resolve a spoken reference such as “the checkout tab” after presenting candidates. The browser extension reports tab ID, URL origin, title, and a short content fingerprint; the relay binds that target to the request; Mac executes only after revalidation.
- **latency:** 300–800 ms for tab listing and identity verification; ask a spoken clarification within 2 seconds when there are multiple candidates. Never perform a click/type on an unverified target.
- **cost:** <$0.005 per request; normally no model call, with model cost only for ambiguous natural-language references.
- **security:** Never read page bodies while resolving candidates; show only origin/title and redacted fingerprints. Reject a command if returned tabId, origin, or fingerprint differs from the bound target. Authenticated content stays in the browser; relay receives opaque target IDs and provenance hashes. Mutations still require existing autonomy/physical approval policy.
- **missing:** Authoritative browser command/session affinity so a requested tab cannot be silently overridden by a stale default; A typed target-lock and revalidation response in the browser bridge; A browser-result guard that rejects mismatched tabId before returning content; A short spoken candidate-list interaction on the pendant

### "“Make every spoken answer accountable: if it was not downloaded and played, retry it or tell me plainly that I missed it.”"
- **useful because:** Today server receipts stop at generation/acceptance, so the system can claim success while the owner heard nothing. Joining artifact generation to authenticated pendant downloaded/started/finished ACKs lets the owner distinguish 'the agent answered' from 'I actually heard it', and automatically recover interrupted briefings without replaying duplicates.
- **path:** relay → pendant → mac → browser
- **model tier:** Use deterministic ACK reconciliation, checksum and idempotency handling for almost all cases. Use a cheaper background model to compress a missed item into a retry notification; use realtime only when the owner asks why playback failed. Mac/browser are evidence sources for the artifact, not trusted as proof of delivery.
- **latency:** ACK ingestion under 200 ms; retry decision within 2 seconds of a checksum/no-audio/interruption event. A missed item should appear in the pendant inbox within one link round, with no duplicate speech if playback_finished was already recorded.
- **cost:** <$0.01 per failed delivery; ordinary successful deliveries are database/event work. Model cost occurs only for a compact recovery summary.
- **security:** ACKs must be authenticated to a device session and deduplicated by event ID plus monotonic sequence. Store opaque artifact IDs, byte/checksum metadata, and playback position—not raw audio in the relay. Do not retry sensitive content into a different surface; apply the existing disclosure policy and require physical approval for any external action implied by the spoken item.
- **missing:** A durable cross-surface join between relay job, audio artifact, and pendant delivery events; An idempotent retry/resume protocol keyed by playback position and artifact checksum; A policy-controlled recovery inbox action for no_audio/interrupted items; A delivery-aware owner-facing receipt that distinguishes generated, downloaded, started, and finished

### "“When I correct you, learn the boundary—not just the answer—and stop making the same kind of mistake on another surface.”"
- **useful because:** Today a correction is usually trapped in one conversation, job, or Mac-local record. The owner has to repeat “don’t do that” after the relay, browser, and pendant disagree. A cross-surface correction model would turn explicit owner corrections into scoped, expiring behavioral constraints, then verify that later decisions actually improved instead of silently accumulating another preference.
- **path:** pendant → relay → mac → browser
- **model tier:** Use deterministic extraction for explicit corrections and deterministic policy checks at execution time. Use the expensive realtime model only to disambiguate the owner’s correction and generate a short explanation; use a cheaper background model to evaluate whether later outcomes support or contradict the learned boundary.
- **latency:** A correction acknowledgement in under 1 second; subsequent policy checks under 100 ms. Never block an urgent physical stop or a clearly owner-approved action on a model-generated lesson.
- **cost:** <$0.01 per correction and near-zero for later checks; background evaluation dominates ongoing cost and can run daily or after a small batch of outcomes.
- **security:** Only explicit owner corrections may create a durable rule; inferred dissatisfaction must remain an observation. Rules need scope (surface, target, action kind), confidence, expiry, and a one-tap/one-press revoke path. Never let a learned rule silently authorize a destructive or external action. Do not export correction text or private context to third-party models; send a redacted rule summary only.
- **missing:** A typed correction event distinct from a general preference or task; A cross-surface rule store with scope, evidence references, confidence, expiry, and supersession; Outcome evaluation that compares later behavior against the correction without changing actions automatically; Owner-facing “what I learned from your correction” and revoke controls on dashboard and pendant

### "“When you choose one thing, show me the important alternatives you rejected and what would have changed your mind.”"
- **useful because:** Current provenance can explain evidence behind an action, but it cannot answer the owner’s harder trust question: whether the system noticed a competing calendar/mail/browser signal, why it suppressed it, and what uncertainty remained. A bounded counterfactual receipt makes judgement inspectable without dumping hidden chain-of-thought.
- **path:** relay → mac → browser → pendant
- **model tier:** Record structured decision facts and matched policy rules deterministically. Use a slower background model to turn those facts into a concise owner-readable explanation; never expose private chain-of-thought or ask the realtime model to reconstruct it after the fact.
- **latency:** No added latency to ordinary execution if the structured receipt is written alongside the decision. Explanation retrieval under 1 second; a spoken answer limited to two alternatives and one decisive condition.
- **cost:** <$0.005 per decision for structured storage; occasional background summarization is the dominant cost.
- **security:** Alternatives may contain sensitive source names or rejected actions, so redact by destination and sensitivity. Never record credentials, page bodies, or speculative actions as if they occurred. Receipts must distinguish observed alternatives, considered policy branches, and actions actually executed. External side effects still require existing confirmation policy.
- **missing:** A typed decision-receipt schema with chosen branch, rejected branches, decisive evidence, uncertainty, and counterfactual trigger; A write path from relay/Mac/browser policy evaluation into durable storage; A retention and revocation link from each receipt to its source evidence; Owner controls for whether receipts are spoken, dashboard-only, or omitted for sensitive decisions


## Changes it proposed to its own stack

### `browser-harness` — Make browser target identity mandatory at the bridge boundary: browser_list_tabs returns a signed target token containing tabId, origin, title digest, and session ID; every read/click/type carries that token; browser result handling rejects any response whose tabId/session/origin differs, and stale default-session fallback is removed. On mismatch, return candidates without page content and require a fresh target selection.
- **owner gets:** The owner will stop getting answers or actions from the wrong browser tab—especially dangerous when YouTube, dashboards, and authenticated sites coexist. Ambiguity becomes an audible question instead of a silent leak or mistaken click.
- effort: Medium: bridge protocol and extension result schema, plus regression tests for stale-session override and tab closure/navigation. No model training required.  ·  risk: Some existing browser jobs will fail closed until they supply the token; recover by re-listing tabs and rebinding. A tab navigation can legitimately change title/URL, so compare origin and session plus a navigation generation rather than exact title alone.
- cost: Negligible runtime/API cost; a few hundred bytes of metadata per command.  ·  latency: Adds one deterministic verification (<50 ms locally) and may add one tab-list round on mismatch.
- security: Substantially reduces cross-tab authenticated disclosure and wrong-target mutation. Target tokens must be opaque, short-lived, and never contain page text or credentials.
- depends on: A browser extension change to echo authoritative tab/session identity in every result; A durable command target token and result validator; Existing browser command lease sweep must be started so stale commands cannot linger

### `hardware` — Add a real wear/presence channel to the next pendant revision: a low-power skin-contact or capacitive sensor with a debounced, signed worn/unworn state and a short local transition history. The relay must treat unworn as a hard boundary for private audio and owner confirmation, while the Mac can continue non-private work. Do not infer wearing from Bluetooth/LTE reachability or button activity.
- **owner gets:** The system could finally know whether speech is going to the owner’s ear or sitting on a desk in front of other people. Private briefings, approvals, and interruption decisions could fail closed instead of guessing from idle time or an absent link.
- effort: High: board revision, enclosure/electrode design, low-power firmware driver, authenticated state events, calibration across clothing/skin conditions, and policy integration on relay/Mac. Prototype with a conductive bezel or optical proximity sensor before committing to production.  ·  risk: False unworn readings could suppress useful audio; false worn readings are the dangerous failure. Recover by requiring a deliberate physical press for private playback when the sensor is uncertain, and expose sensor confidence rather than pretending it is binary.
- cost: Roughly $1–$4 in components/assembly for a simple capacitive/proximity channel, plus tens of milliwatts or less when sampled intermittently; meaningful one-time enclosure/PCB cost.  ·  latency: 100–500 ms debounce on transitions; no ongoing conversational latency once state is stable.
- security: Improves privacy and physical consent, but the worn state itself is sensitive telemetry. Keep raw sensor data local; export only signed state transitions with coarse timestamps and allow the owner to disable remote presence reporting.
- depends on: A hardware sensor absent from the current pendant; A signed presence-state event in the relay protocol; An explicit policy mapping worn/unworn/unknown to audio disclosure and physical approval; A recovery path for sensor uncertainty that never silently speaks private content


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities and one concrete harness change: a trust-gated morning brief, fail-closed browser target selection, delivery-accountable/self-healing speech, and mandatory browser target tokens/result validation. The live browser mismatch (requested dashboard tab, received YouTube content) is now treated as a security defect, not a model ambiguity. I still need implementation work—not another discovery call—to wire durable joins between routine/job/artifact/device ACKs, enforce browser target affinity in the extension, and expose the owner's explicit policies for degraded briefs and spoken disclosure. The owner’s current timezone facts also conflict (America/Chicago in owner memory versus authoritative Mac routine zone America/New_York), so no new schedule promise should silently choose between them.

**Biggest unknown:** Which timezone and disclosure policy the owner explicitly wants for spoken scheduled briefs; the system has authoritative Mac routine time but not the owner's physical timezone, and the owner has not answered whether partial/private brief content may be spoken.

