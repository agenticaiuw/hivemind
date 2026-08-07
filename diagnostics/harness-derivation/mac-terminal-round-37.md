# Harness derivation — mac-terminal — round 37

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do that, and don’t tell me it worked unless you can verify the result.”"
- **useful because:** Today /observe shows a critical false-success condition: Accessibility is not trusted for the running agent, so UI clicks and typing can report success while doing nothing. This capability turns the pendant into a trustworthy completion channel: it preflights the Mac, chooses the reachable surface, verifies a concrete postcondition independently, and reports failure or recovery rather than a misleading success.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** background for planning and verification recipes; deterministic checks and Mac observation for most jobs; realtime only to acknowledge the spoken request and deliver the short result
- **latency:** 2–5 seconds for preflight plus deterministic verification; up to 30 seconds for a fallback or retry, with the pendant giving an immediate 'working' acknowledgement
- **cost:** Usually one background planner call (roughly 2k input tokens, small output; about $0.01 or less depending on model pricing); deterministic observe/receipt calls dominate neither cost nor latency. Vision fallback is the expensive path and should be opt-in per job.
- **security:** The command still runs under the owner's deliberate FULL_CONTROL_MODE with no gates. Verification must not expose private page contents to the relay unnecessarily: return typed predicates and hashes, keeping evidence local on the Mac. Browser mutations remain draft/approval semantics where applicable. A failed verification, timeout, or ambiguous state must be reported plainly and never converted into success.
- **missing:** A typed postcondition/verification schema shared by mac-planner, browser bridge, and relay (for example file hash, app state, URL/title, process state, or reversible setting); A preflight health contract that marks UI automation unavailable when Accessibility/input reachability is false and permits shell/browser fallback; Receipt fields for attempted, verified, unverified, fallback, and recovered outcomes, plus durable retry/repair jobs; A relay-to-pendant result event that can speak a concise receipt and expose detailed evidence in the dashboard

### "“I’m stopping here—save exactly where I am and let me resume this later from the pendant.”"
- **useful because:** Today the owner can leave a job record or a browser tab behind, but cannot preserve a coherent, cross-device stopping point: the exact open tab and evidence, Mac working files and app state, the last confirmed step, unresolved decisions, and the next safe action. This gives them a reliable pause/resume boundary instead of reconstructing their train of thought.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background model to compress and label the handoff packet; deterministic collectors for tab metadata, Mac job receipts, file paths, and timestamps; realtime only for the spoken save/resume interaction
- **latency:** A spoken “save here” acknowledgement in under 2 seconds; packet assembly in under 10 seconds. Resume should present the packet immediately, then spend up to 30 seconds revalidating stale state before proposing the next action.
- **cost:** One small background summarization call per saved handoff (roughly 1–3k input tokens and a short output, typically cents or less); most collection and revalidation is local and deterministic. Storage is a small JSON packet plus optional local screenshots or hashes.
- **security:** Private tab content and local paths remain on the Mac unless the owner explicitly asks for relay sync; the relay stores only an encrypted/minimal index and expiry. Never restore or submit a browser mutation automatically after state changed; show stale fields and require the normal owner decision for consequential actions. Include deletion and retention controls.
- **missing:** A first-class handoff object with immutable checkpoint, owner-visible title, source surface, last-confirmed step, unresolved questions, next-action candidates, TTL, and stale-state status; Mac collectors for active project/file/app context and browser collectors for selected tab DOM excerpts, URL/title, and evidence hashes; A revalidation/resume protocol that compares the checkpoint against current tabs, files, jobs, and permissions before offering continuation; Pendant commands and dashboard UI for save, list, resume, edit, and delete handoffs, with encrypted local-first storage and relay indexing


## Changes it proposed to its own stack

### `mac-harness` — Add a non-blocking execution assurance layer around every Mac job: snapshot /observe before execution; classify input reachability, Accessibility, screen recording, browser bridge presence, and shell availability; attach an explicit postcondition recipe to the plan; execute unchanged under FULL_CONTROL_MODE; then re-observe and evaluate the predicate. If UI reachability is false, mark UI steps unavailable and automatically select a shell or browser strategy when equivalent; if no predicate can be checked, return unverified rather than success. Persist before/after evidence, fallback attempts, and recovery hints in the job journal.
- **owner gets:** The owner gets honest answers. A request will no longer sound completed when the agent's UI events were accepted by the harness but never reached the screen, and common failures can recover through another machine or surface without making the owner repeat themselves.
- effort: Medium: typed predicate model, pre/post hooks in executor, strategy fallback rules, journal schema, dashboard rendering, and relay receipt mapping. No change to the owner's maximum-access policy.  ·  risk: Some actions have no observable postcondition and will become 'unverified', which may feel less convenient; predicates can be stale or too weak. Recover by retaining raw evidence and allowing a follow-up verification command. Do not claim verification from the action receipt alone.
- cost: Negligible API cost for deterministic checks; one background planner call only when a predicate must be synthesized. Small local journal growth; add retention/compaction.  ·  latency: Typically <1 second for /observe and deterministic checks; fallback or vision adds seconds and should be visible in the receipt.
- security: No new restriction or approval gate. Keep page text and command output local where possible; relay receives typed status, hashes, and minimal evidence rather than full private content.
- depends on: A shared typed postcondition schema across Mac, browser, and relay; Existing /observe, /journal, and receipt plumbing; A durable retry/fallback job record

### `context` — Create a local-first cross-surface checkpoint store and protocol. On a pendant save command, ask Mac and browser agents for typed snapshots (active job and receipt, selected tabs and DOM/evidence hashes, focused project/files, pending decisions), have the relay assign a checkpoint ID and encrypt only the minimal index, and expose a revalidation endpoint that marks each fact fresh, changed, inaccessible, or deleted before resume. Resume returns a proposed next step, never an unverified continuation.
- **owner gets:** They can stop work on the Mac, walk away with only the pendant, and later continue from the real point they reached instead of hunting through tabs, files, and conversation history.
- effort: Medium-high: protocol and schema, local encrypted storage, browser/Mac collectors, relay index, pendant utterances, and dashboard controls.  ·  risk: A snapshot may include more context than intended or become stale. Mitigate with explicit selection, short TTLs, redaction, per-field provenance, local deletion, and a visible stale-state review before resuming.
- cost: Low recurring model cost; storage is modest. Encryption and local indexing add implementation complexity but no meaningful runtime expense.  ·  latency: Save is parallel and should complete in a few seconds; resume revalidation adds roughly 1–5 seconds before showing the owner the continuation plan.
- security: Improves privacy versus sending full context to the cloud by keeping content local and syncing only encrypted metadata/hashes; still requires careful key management and deletion semantics.
- depends on: Typed cross-surface snapshot schema; Authenticated Mac and browser collectors; Relay durable state with encryption and TTL; Pendant command/result events; Dashboard support for provenance and stale-state review


## What it asked for

_Nothing._
## Its own summary

Discovered live execution truth: /ops/status reports FULL_CONTROL_MODE and relay online, but /observe reports Accessibility=false, input reachability failed, and explicitly warns that UI actions can report success while doing nothing. Browser bridge is offline with 2 pending commands. I proposed a new cross-surface capability, “do it and verify it,” plus a Mac-harness execution-assurance change using preflight health, typed postconditions, independent verification, truthful unverified receipts, and shell/browser fallback—without adding gates or reducing owner access. I also notified mac-planner.

**Biggest unknown:** The newly granted Mac diagnostic schemas exist but have no implementation, so I cannot independently collect fresh OS/battery/network/process facts through them. I still lack the concrete local-agent job lifecycle/observability contract and authenticated access to /jobs, /logs, /journal, and /routing; those are needed to wire durable retries and verified receipts rather than merely specify them.

