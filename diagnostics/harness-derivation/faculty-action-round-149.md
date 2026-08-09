# Harness derivation — faculty-action — round 149

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device inventory** — The live relay inventory currently shows Safari (9 tabs) and home-macbook-bridge online, but no nRF9160 pendant; the only mobile device is offline since 2026-07-31. This means USB-connected pendant claims are not yet reflected in relay registration, so USB presence work can only be a Mac-local prototype until serial inventory/heartbeat is exposed.
  - evidence: discover(devices) in round 149 returned Safari on MacIntel online, home-macbook-bridge online, and cloudflare-contract-test mobile offline; no pendant entry.

## Capabilities it proposed

### "“Fill out this form using the private details already in my browser, show me exactly what will be submitted, and only send it after I approve on the pendant.”"
- **useful because:** This is the highest-value safe action loop: the Mac/browser can use authenticated sessions and secrets without exposing them to the relay, while the pendant gives an unmistakable physical commit. The owner gets completed forms without surrendering browser contents or worrying that a conversational misunderstanding sent them.
- **path:** unified → faculty-judgement → mac-planner → browser-extension → faculty-perception → faculty-action → relay-realtime
- **model tier:** background for field mapping and draft explanation; realtime only for the owner's brief spoken confirmation; local Mac/browser execution for all secrets and submission
- **latency:** Draft in under 10 seconds; field review under 3 seconds after the owner asks; submission and independent verification under 15 seconds. If verification fails, report unknown rather than claiming success.
- **cost:** Usually one background planning call plus one short realtime turn; roughly $0.03–$0.15 depending on form complexity. Browser and Mac work dominate latency, not tokens.
- **security:** Form values, page text, cookies, and uploaded documents stay on the Mac/browser. Relay receives only a redacted field schema, human-readable summary, digest, and final verification receipt. Submission must be staged, expire, and require the pendant's physical transaction latch; never put secrets in the approval envelope. Destructive or legally consequential forms should default to explicit approval even if policy later permits lower-risk actions.
- **missing:** A browser-side redaction-and-field-schema exporter that can describe values without exporting them; A single staged-submit operation spanning browser sessions, physical_transaction_approval_latch, and verify_operation_step; A review artifact the pendant can identify by digest without speaking private field values

### "“When I say ‘take care of this’, keep the task alive across my Mac going to sleep or losing the browser, resume from the last verified step, and tell me only when you need a decision.”"
- **useful because:** Today a multi-step action can stop halfway and leave the owner unsure whether to retry, duplicate a submission, or inspect several apps. A durable, resumable action record would let the mind act like an assistant rather than a one-shot macro: every step has a precondition, an executor receipt, an independent postcondition check, and a safe resume or stop decision.
- **path:** unified → faculty-judgement → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** background model for decomposition, retry policy, and summarizing exceptions; realtime only to ask the owner about an actual ambiguity; local harness for deterministic steps
- **latency:** A healthy step should begin within 2 seconds of Mac availability. On reconnect, recover the ledger in under 5 seconds. Never silently retry a non-idempotent step; pause and ask instead.
- **cost:** About $0.01–$0.08 per resumed task, mostly one planning/reconciliation call; deterministic retries and verification are local.
- **security:** Persist only step metadata, digests, and redacted receipts; keep page contents and secrets in the local browser. Each step declares idempotency and risk. Expired approvals cannot resume a commit step. A crash must leave the task in unknown state, not mark it completed; the pendant should receive only a short status and a digest.
- **missing:** A durable step runner that persists preconditions, idempotency keys, lease expiry, and resume cursor; An executor contract that returns structured receipts including attempt id and whether a mutation may have happened; A reconnect reconciler that calls verify_operation_step before resuming after interruption

### "“Watch for this condition in my browser, and when it becomes true, prepare the next action—but never commit it until I approve on the pendant.”"
- **useful because:** The owner can delegate waiting instead of repeatedly checking a page: a delivery status, appointment opening, invoice change, or application result becomes a staged action at the moment it is actually observed. The relay can watch while the Mac sleeps, the browser can use its authenticated session, and the pendant remains the only physical commit gate.
- **path:** unified → faculty-judgement → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Cheap background/scheduled model for polling cadence and change classification; local browser selectors and deterministic comparison for observations; realtime only when reporting a meaningful transition or asking for approval
- **latency:** Use adaptive polling (minutes when unchanged, seconds around an expected window) and notify within one polling interval. Stop after expiry or a bounded observation budget. Staging should take under 10 seconds after a detected change.
- **cost:** Approximately $0.01–$0.10 per watch-day depending on cadence; browser polling and relay storage dominate, so unchanged pages should not invoke a model.
- **security:** Watch definitions contain URLs/selectors but not extracted secrets. Browser-side comparison should emit a hash or minimal matching snippet. Each trigger records timestamp, URL, session, and before/after digest; stale pages or changed selectors disable the watch. Actions remain staged until physical approval and must be independently verified after commit.
- **missing:** A durable watch resource with schedule, expiry, backoff, selector/hash comparison, and pause-on-authentication failure; A relay-to-browser wake path that can poll an already-open authenticated tab without exporting page contents; A typed trigger-to-action binding that produces a physical approval envelope and postcondition verification receipt

### "“Complete the sign-in or passkey challenge in the browser, but make me confirm the exact site and account on the pendant before any credential is used.”"
- **useful because:** The owner could safely delegate the frustrating part of authentication without handing the relay a password, passkey, cookie, or one-time code. The browser keeps the credential local; the Mac drives only the allowed origin; the pendant gives a physical, human-readable confirmation that prevents a malicious or mistyped site from receiving a credential. This enables the hive to act across the browser session and wearable security boundary in a way neither node can provide alone.
- **path:** unified → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → relay-realtime
- **model tier:** Local deterministic browser protocol handling for origin and account display; background model only to explain an unfamiliar challenge; realtime model only for the owner's short confirmation conversation
- **latency:** Detect and summarize the challenge within 2 seconds, wait indefinitely for the owner's deliberate pendant gesture, and complete the browser ceremony within 5 seconds after approval. Abort on navigation, origin, account, or challenge-hash change.
- **cost:** Under $0.02 per ceremony in the normal case; most work is local browser/WebAuthn APIs and no page contents need model processing.
- **security:** The relay must never receive credentials, passkeys, cookies, OTP values, or challenge secrets. The browser extension signs a canonical tuple of origin, relying-party ID, account label, action, and challenge digest; the pendant approves only that digest and expiry. Require a new approval after any redirect or tab replacement, refuse iframe-origin ambiguity, and log only redacted provenance.
- **missing:** A browser-extension WebAuthn mediation protocol that exposes origin/account/challenge metadata without credential material; A pendant approval envelope specialized for origin-bound authentication, with replay and redirect refusal; A Mac-local verifier that confirms the active tab origin immediately before and after the ceremony

### "“If a logged-in site shows a suspicious sign-in or account change, warn me on the pendant, preserve a redacted evidence bundle locally, and offer to lock down only that account after I approve.”"
- **useful because:** The owner gets rapid, actionable protection instead of a passive notification buried in a browser tab. The browser can see the authenticated security page, the Mac can preserve timestamps and navigate account controls, the relay can remain reachable while the Mac is unattended, and the pendant provides an unmistakable approval boundary for sign-out, session revocation, or password/passkey rotation.
- **path:** unified → browser-extension → mac-planner → mac-vision → faculty-perception → faculty-judgement → faculty-action → relay-realtime
- **model tier:** Deterministic local rules detect known security events; background model classifies unfamiliar notices and drafts a short explanation; realtime only for the urgent spoken alert and approval dialogue
- **latency:** Alert within one browser poll interval, target under 30 seconds. Evidence capture under 5 seconds. Containment begins only after approval and must report verified, failed, or unknown within 20 seconds.
- **cost:** Near zero for known event patterns; $0.01–$0.05 only when unfamiliar text needs classification. Storage is a few KB per incident plus optional local screenshots.
- **security:** Evidence stays on the Mac and is encrypted/retained for a bounded period; relay receives only event type, site identity, digest, and severity. Never transmit passwords, recovery codes, or page screenshots by default. The system must distinguish a genuine account control from a phishing page by origin and certificate/session metadata, and never auto-revoke every account as a panic action.
- **missing:** A browser security-event observer covering login alerts, recovery-email changes, new devices, and suspicious payment/account activity; A local encrypted incident bundle with retention and redaction policy; Typed containment actions (revoke session, sign out, freeze, rotate credential) with independent verification and pendant approval

### "“When I hand a task from my Mac to another person, prepare a least-privilege handoff: the exact files or links, what they may change, an expiry, and a way for me to revoke it from the pendant.”"
- **useful because:** The owner can delegate real work without sharing an entire folder, browser session, or standing account access. The Mac assembles the handoff, the browser creates a narrowly scoped share or draft, the relay tracks expiry and revocation, and the pendant makes revocation available even when the owner is away from the Mac.
- **path:** unified → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-action → relay-realtime
- **model tier:** Background model for summarizing scope and detecting overbroad permissions; deterministic local tooling for file/link selection, expiry, and revocation; realtime only for a concise confirmation or urgent revoke
- **latency:** Generate a handoff in under 15 seconds and propagate a revoke in under 10 seconds when the Mac/browser is online. If offline, queue the revoke and mark access as potentially live rather than claiming it is closed.
- **cost:** $0.02–$0.10 per handoff depending on scope analysis; file hashing, browser operations, and revocation polling dominate rather than model tokens.
- **security:** Never expose browser cookies or broad filesystem paths. Use capability-scoped links or copies, redact secrets, record recipient and expiry, and require explicit approval for external sharing. The pendant carries only an opaque handoff ID and revoke nonce. Independent verification must confirm the share is disabled, otherwise status is unknown.
- **missing:** A least-privilege handoff builder for local files and browser resources; Provider-specific share/revoke adapters with postcondition checks; A durable revocation registry reachable from relay and pendant, including offline expiry semantics


## Changes it proposed to its own stack

### `interaction` — Add a pendant-to-Mac action presence channel: while the nRF9160 pendant is physically attached over its live USB serial link, the Mac agent exposes a short-lived, device-bound presence token to faculty-action. High-risk staged actions may use it only as an additional freshness signal; it never replaces the deliberate physical transaction approval latch. On detach, token expiry, or serial reset, pending commits become needs-reconciliation and the Mac must verify state before offering resume.
- **owner gets:** A stale approval should not remain usable because the owner walked away, closed the lid, or a second person later used the Mac. The owner gets a clear “this approval is no longer live” boundary today, using hardware that is actually connected, without sending browser secrets to the pendant.
- effort: Medium: serial heartbeat framing and key derivation, local agent token cache, action policy hook, and tests for detach/reconnect races. No firmware flash required for an initial USB-only prototype; LTE binding can follow later.  ·  risk: A dropped USB link could pause a task unexpectedly, so only commit steps pause; drafts and reversible steps continue. Never infer physical proximity from an old token. Recovery is explicit re-verification plus a new approval, not automatic replay.
- cost: Negligible API cost; roughly 1–2 KB RAM in the local agent and under 1 KB of periodic serial traffic. Hardware cost $0 using the connected pendant.  ·  latency: Heartbeat detection under 2 seconds; no added latency to ordinary draft actions, and under 100 ms to gate a commit.
- security: Improves freshness and replay resistance, but is not an identity proof and must be documented as such. Secrets remain Mac-local; the pendant receives only opaque token status and LED/audio cues.
- depends on: A stable USB serial heartbeat for /dev/cu.usbmodem00096003658*; An amendment to physical_transaction_approval_latch defining presence as a freshness condition, not consent; The existing actionRisk/policyRouter seam and verify_operation_step for post-detach reconciliation


## What it asked for

_Nothing._
## Its own summary

Round 149 produced three distinct owner-facing capabilities: (1) private browser form completion with redacted review and pendant-gated submission, (2) durable resumable multi-step actions that reconcile unknown state before retrying, and (3) condition-triggered browser watches that stage an action when a page changes. I also proposed a USB pendant-to-Mac freshness channel that invalidates stale approvals without replacing physical consent. Live discovery shows the Mac bridge and Safari online but no registered pendant, despite the hardware being physically testable over USB.

**Biggest unknown:** The missing execution seam is not model intelligence: it is a durable step/watch runner with structured mutation receipts, browser-local redaction/comparison, and a Mac-local USB serial heartbeat. Until those exist, I cannot honestly promise resumable commits or presence-gated action; I need those implemented, plus the owner to decide which action classes may ever auto-stage versus always require approval.

