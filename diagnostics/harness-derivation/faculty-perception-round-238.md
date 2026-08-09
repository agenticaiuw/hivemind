# Harness derivation — faculty-perception — round 238

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live mac observability and permissions** — At 2026-08-09T01:55Z the Mac agent is online and ready: Accessibility and Screen Recording are granted, all listed automation grants are granted, browser extension is online with two Safari tabs, relay is reachable and D1-backed. No pendant appears in the live device inventory; registered devices are home-macbook-bridge online and cloudflare-contract-test offline.
  - evidence: GET /ops/status HTTP 200 and discover(devices) in this round; /ops/status reports permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browserExtension.online=true, relay.reachable=true.

## Capabilities it proposed

### "Tell me what is true right now, and refuse to claim anything the system cannot actually prove."
- **useful because:** The current aggregate snapshot mixes live state, stale state, Mac-authored opinions, count-capped history, and relay delivery that is not playback. This gives the owner a concise answer with each claim tagged by source, observed-at time, freshness, and confidence, and explicitly says when absence is not evidence. It is the single most useful perception capability because every action and spoken answer can stop treating 'completed' as 'heard' or 'online' as 'reachable'.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background for assembling and normalizing evidence; realtime only for the final short spoken answer
- **latency:** under 2 seconds from live Mac/relay reads; browser and pendant branches may return unknown rather than blocking
- **cost:** roughly one cheap background model call per request; dominated by the existing /ops/snapshot export, not new model tokens
- **security:** Do not expose page text, secrets, or bearer credentials in the spoken result. Preserve source-level access controls and label Mac-derived pendant fields as opinions. Any action suggested from an uncertain claim requires owner confirmation.
- **missing:** A typed evidence-claim contract with observedAt, source, freshness policy, and negative-evidence semantics; A live pendant branch once a pendant registers and emits its reality beacon; A relay-side reader that distinguishes socket bytes from device playback

### "Before you act on anything I am looking at, tell me whether the claim came from my authenticated browser or from an untrusted relay fetch, and refuse to act when the evidence is ungrounded."
- **useful because:** The relay's read_web_page returns untrusted text with no ID, hash, URL-bound capsule, or persistence; the Mac extension can produce grounded evidence but its provenance routes are currently unmounted. This creates a hard safety boundary: research may inform speech, but account changes, purchases, messages, and form submissions require a grounded browser observation tied to the exact tab and current content.
- **path:** browser → mac → relay → pendant
- **model tier:** background policy/evidence classifier; realtime only for the owner's confirmation dialogue
- **latency:** under 1 second for cached provenance checks; up to 3 seconds for a fresh browser snapshot
- **cost:** low; hashing and capsule lookup dominate, with model use only when classifying whether a requested action depends on page content
- **security:** Authenticated page data remains on the Mac by default. Store redacted capsule bodies and hashes, never credentials. Require explicit confirmation for destructive or financial actions even with grounded evidence. Fail closed on revoked, expired, or relay-only evidence.
- **missing:** Mount local browserProvenance routes and wire every browser mutation/read to recordExtraction; Return a stable content hash/correlation ID from relay read_web_page when it is used for research, while keeping it permanently non-authoritative for actions; An action-gate that requires a non-expired, non-revoked capsule linked to the exact command and tab

### "Tell me when two parts of my system disagree about a fact, showing which source is newer and which one is merely a machine guess."
- **useful because:** The live system already has contradictory machine-derived timezone memory versus the Mac's authoritative America/New_York, and aggregates can also disagree about browser, relay, job, and device state. A discrepancy detector would surface contradictions before they silently steer routines or actions, instead of asking the model to average them or choosing by confidence alone.
- **path:** mac → relay → browser → pendant → dashboard
- **model tier:** background deterministic comparator first; cheap model only to explain the conflict in one sentence
- **latency:** run on each snapshot refresh or within 60 seconds of a source change; spoken report under 2 seconds when requested
- **cost:** negligible for normalized field comparison; occasional cheap explanation call
- **security:** Do not overwrite facts automatically. Preserve source.origin, observedAt, and authority scope; redact sensitive values in dashboard diffs. Owner confirmation is required to change pinned preferences or trigger actions based on a conflict.
- **missing:** A common normalized observation schema with authority scope (Mac-resolved, owner-stated, relay-reported, device-reported); A comparator over memory projection, machine context, browser state, relay registry/jobs, and pendant beacon; A dashboard and spoken formatter that distinguishes contradiction from expected scope differences

### "Why did you believe that, exactly? Replay the evidence chain for this answer, including what each surface observed, what was discarded, and where uncertainty entered."
- **useful because:** Today the owner can inspect logs or a truncated snapshot, but cannot reconstruct why a realtime answer or action was chosen across relay, Mac, browser, and pendant. An epistemic replay makes mistakes explainable and correctable: it separates observed facts from model inferences and exposes when a stale or untrusted source crossed into a decision.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** background deterministic event reconstruction with a cheap summarizer; realtime only for the owner's spoken question
- **latency:** under 3 seconds for a recent turn; older replay can be asynchronous with a queued result
- **cost:** moderate storage and indexing cost; low model cost because the primary artifact is structured events, not regenerated reasoning
- **security:** Never expose hidden chain-of-thought or secrets. Store tool inputs/outputs as redacted evidence envelopes, retain hashes and provenance, and show only concise decision factors. Owner confirmation is required before replaying sensitive browser or message content aloud.
- **missing:** A cross-surface decision-envelope event format linking turn, observation, inference, action, and outcome; Relay and Mac emitters for tool results and model routing decisions, with redaction before persistence; A dashboard/realtime query that renders evidence lineage without claiming private reasoning

### "Require my physical pendant to approve a sensitive action, and show me which browser tab, Mac process, and relay request that approval is authorizing."
- **useful because:** Today the relay WebSocket uses the admin key, browser sessions and Mac jobs are separately authenticated, and no device-originated approval binds an action to the owner's physical presence. A short press on the worn device could become a human-presence challenge that prevents a stale browser tab, compromised relay session, or mistaken model plan from sending mail, buying, deleting, or changing an account.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** realtime for the immediate spoken challenge; deterministic cryptographic verification and background policy evaluation for the action
- **latency:** challenge round trip under 2 seconds when connected; fail closed and explain offline when the pendant is absent
- **cost:** low per approval; dominated by a small durable challenge ledger and one relay round trip, not model tokens
- **security:** Use per-device scoped credentials and nonce-bound signed approvals, never the current shared admin key. Display target, irreversible effects, and expiry on the Mac/browser before the button press. Prevent replay, bind approval to exact action arguments and tab/session, and require a fresh challenge for high-risk actions.
- **missing:** Firmware signing/approval primitive and a local button gesture that survives intermittent connectivity; Relay challenge/verification endpoints and replacement of the pendant's admin-key WebSocket identity with scoped credentials; Mac/browser action middleware that pauses execution and renders the exact canonical action digest

### "Show me a rehearsal of what will change across my Mac, browser, relay, and pendant before you do it, including conflicts and a one-step rollback plan."
- **useful because:** Existing planning and undo are surface-local and action completion can be reported before the pendant or browser actually reflects it. A cross-surface rehearsal would resolve the exact current targets, predict side effects, identify conflicting pending work, and require one approval over a canonical plan; after execution it would verify each surface and expose which rollback steps are actually available.
- **path:** mac → browser → relay → pendant → dashboard
- **model tier:** background planner for the dry run; deterministic validators for target resolution, conflicts, and rollback coverage; realtime only to summarize and ask for approval
- **latency:** under 5 seconds for ordinary Mac/browser changes; long research or multi-step plans return a pending rehearsal with progress
- **cost:** moderate: extra read-only probes and a cheap planning call; substantially cheaper than recovering from a wrong cross-surface action
- **security:** Rehearsal must be read-only and must not trigger page navigation, mail sends, or relay announcements. Canonicalize and hash the approved plan, expire it quickly, revalidate targets immediately before execution, and require renewed confirmation if any target changed.
- **missing:** A cross-surface dry-run protocol with canonical target snapshots and conflict detection; Rollback contracts that describe what is reversible, what is compensating rather than undoable, and what requires owner confirmation; A pendant-visible approval/verification state once the device is available


## Changes it proposed to its own stack

### `model-routing` — Install a perception gate before every realtime answer and action plan: deterministic checks first validate source authority, freshness, device presence, and evidence class; route unresolved interpretation to a cheap background model; allow the realtime model to speak only the resulting claims and uncertainty labels. Cache the normalized observation set for one turn so it is not re-sent and re-inferred repeatedly.
- **owner gets:** The pendant will stop confidently saying that a Mac job completed, a relay announcement was heard, or a machine-written preference is the owner's intent. Short answers become more trustworthy without making every routine or voice turn pay for an expensive model.
- effort: Medium: define observation/claim types, add a preflight middleware to realtime tool results and action planning, and write tests for stale, absent, contradictory, and ungrounded evidence.  ·  risk: Overly strict gating could make the assistant say unknown too often. Recover by logging the rejected claim with its reason and allowing an explicit owner override; never silently downgrade an unknown to false.
- cost: Reduces realtime-token spend and repeated context transmission; adds a small deterministic CPU/cache cost and occasional cheap background calls.  ·  latency: Usually decreases latency; a background explanation may add up to 1–2 seconds only for contradictions or missing provenance.
- security: Improves security by preventing untrusted relay page text and stale state from authorizing actions; does not broaden permissions.
- depends on: A normalized evidence contract with source, authority scope, observedAt, freshness, and confidence; A mounted browser provenance path for grounded browser claims; A real pendant playback event when a pendant exists


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: Mac agent is online and fully permission-ready (Accessibility, Screen Recording, automation), Safari bridge is online with two tabs, relay is reachable and D1-backed, and no pendant is registered. Recorded three non-duplicate directions: a source/freshness/authority truth contract, a grounded-evidence action boundary for browser claims, a cross-surface contradiction detector, plus a model-routing perception gate. The owner now gets a system that can refuse unsupported claims instead of merely reporting more status.

**Biggest unknown:** The pendant remains physically absent from the relay registry, so device-reported liveness, capture quality, and playback truth cannot yet be verified. I still need the normalized evidence contract, mounted browser provenance wiring, and—when the pendant exists—a real device playback event; otherwise every pendant delivery claim must remain unknown.

