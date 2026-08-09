# Harness derivation — faculty-action — round 207

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When a risky action was approved but its result is uncertain, stop retrying and tell me exactly what is known, what is not, and offer one safe recovery choice from the pendant."
- **useful because:** The worst failure is a duplicate send or purchase after a timeout. This turns an ambiguous receipt into a safe human decision instead of silent retries or false success.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Realtime only for the short owner-facing explanation; background relay state machine and verification use a cheaper model or deterministic code.
- **latency:** Initial unknown verdict under 3 seconds after executor return; recovery choice acknowledged within 1 second of pendant input.
- **cost:** Usually <$0.01 per incident; most work is deterministic state handling, with a small model call only for the concise explanation.
- **security:** Never retry an irreversible action automatically after unknown. Show only a redacted action summary on the pendant; keep secrets and page contents on Mac/browser. Recovery choices must be bounded and require the existing physical approval latch.
- **missing:** A durable unknown-outcome state machine joining operation_id, attempt_id, executor receipt, and independent verification provenance; A typed recovery vocabulary (inspect, retry-if-idempotent, cancel) and policy metadata for action idempotency; Pendant rendering amendment to tactile_action_outcome_beacon for unknown-plus-recovery choices

### "Let the pendant remember the exact moment I asked for an action, then let me say 'continue' later and have the Mac reopen the same project, browser session, and draft—only if every referenced state is still fresh."
- **useful because:** A thought captured while walking should resume at the desk without making me reconstruct tabs, files, and context. Freshness gates prevent acting on a stale page or changed draft.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Background model builds a compact context bundle; realtime handles only the resume phrase and confirmation.
- **latency:** Capture immediately; resume context assembled in under 5 seconds, with stale components called out before any mutation.
- **cost:** <$0.02 per resume; hashes and freshness checks are deterministic, with model cost limited to summarization.
- **security:** Store opaque references and hashes, not page secrets or full audio by default. Never replay a mutation from a bookmark; reopening and drafting are safe, sending requires existing approval.
- **missing:** A cross-surface context capsule schema linking pendant event, active project, browser session, file hashes, and expiry; A stale-component resolver that can reopen only verified references and asks before replacing changed drafts; A pendant input path for selecting among multiple saved moments once the planned rotary encoder exists

### "Before sending a message or submitting a form, warn me if the person, account, or destination does not match the identity I named—even when the page is already open—and let me approve the exact recipient from the pendant."
- **useful because:** A polished automation that sends sensitive material to the wrong Alex, account, or environment is worse than no automation. The browser knows the live destination, the Mac knows the intended contact context, and the pendant is the last unmistakable place to stop it.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Realtime for a short risk explanation; deterministic identity matching and destination comparison do the primary work.
- **latency:** Under 1 second for a pre-submit risk check and under 2 seconds for a pendant warning.
- **cost:** Usually below $0.01 per submission; most checks are local hashes, structured destination fields, and contact matching.
- **security:** Never upload message bodies or secrets to the relay. Compare redacted recipient identifiers and origin metadata. A mismatch must block submission until a deliberate physical approval references the exact destination digest.
- **missing:** A canonical destination-identity record spanning contacts, browser origin/account, and intended recipient; Browser pre-submit interception that exposes destination metadata without exposing field secrets; A pendant-safe summary format for distinguishing names, domains, account labels, and environment (production/test)

### "When an automation needs to disclose private information to a website or message recipient, show me exactly which categories of data will leave the Mac and let me approve only that bounded disclosure, not the whole workflow."
- **useful because:** Today approval tends to mean 'do the action.' This gives the owner a meaningful data boundary: a form may proceed with a shipping address while refusing notes, credentials, or unrelated personal fields.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** A cheaper background classifier labels fields locally; realtime only summarizes the proposed disclosure and handles a narrow owner response.
- **latency:** Field classification under 2 seconds; pendant summary under 3 seconds; no disclosure before approval.
- **cost:** Under $0.02 per sensitive submission, dominated by local classification; no model call is needed for known field types.
- **security:** Secrets and raw values remain on the Mac/browser. The relay receives only category labels, destination digest, and an approval nonce. Approval expires when the page, destination, or field set changes.
- **missing:** Field-level sensitivity and provenance extraction in the browser bridge; A disclosure manifest with category, destination, reason, digest, and expiry; An approval primitive that binds to a disclosure manifest rather than merely an action


## Changes it proposed to its own stack

### `integration` — Build a bench-only commissioning run that correlates a real pendant button event, ESP32 bridge audio loopback, Mac timestamps, and the resulting relay pipeline record into one signed test report. It should run read-only except for playing a test fixture, fail closed when any clock or device identity is missing, and never treat USB as product transport.
- **owner gets:** Today the hardware is physically on the Mac but disconnected from LTE; this gives the owner a one-command answer to 'did the complete worn-device audio/action path work just now?' instead of trusting labels or isolated logs.
- effort: Medium-high: serial readers and clock correlation are missing, plus a bounded fixture runner and report schema; no firmware mutation or flashing.  ·  risk: A false pass could hide dropped packets or misattributed devices. Require packet counters, explicit port identities, and audio_path_probe evidence; reports must say bench-only and unknown when correlation is incomplete.
- cost: Negligible API cost; one 5–30 second fixture run. No new hardware cost; uses the nRF9160 DK, ESP32 bridge, and existing audio components.  ·  latency: 5–30 seconds for a full report; a quick connectivity check under 2 seconds.
- security: Read-only serial inspection and synthetic audio only; no microphone open, no secrets printed, and no LTE credentials touched.
- depends on: mac-terminal's granted bounded USB/serial diagnostics capability; audio_path_probe; A durable cross-device test correlation ID accepted by the relay pipeline; Owner-approved firmware test mode that emits counters without flashing

### `context` — Add a durable cross-surface identity-and-data ledger: every browser submission candidate records destination identity, account/environment, field-category manifest, source provenance, approval digest, and final postcondition provenance. Keep values on the Mac; relay and pendant receive only redacted labels and hashes. Reject execution if any of those bindings change between preview and submit.
- **owner gets:** The owner gets an automation that can explain not only what it did, but who it contacted and what classes of personal information crossed the boundary—preventing silent drift when a tab, account, or form changes.
- effort: High: requires browser bridge instrumentation, Mac-local redaction, durable schema/versioning, and enforcement immediately before submission.  ·  risk: Overblocking can frustrate the owner; unknown identity or sensitivity must fail closed, with a one-step path to inspect the changed page rather than silently proceeding.
- cost: Low runtime API cost and storage overhead; one compact manifest per sensitive submission. Engineering cost is primarily browser instrumentation and policy testing.  ·  latency: Adds roughly 100–500 ms for local manifest comparison; remote verification should not be on the critical secret-handling path.
- security: Improves security by ensuring the relay never receives raw secrets or private field values. Hashes and labels can still be sensitive, so retain short expiry and strict access controls.
- depends on: Browser bridge support for pre-submit interception and structured destination metadata; Mac-local sensitivity classification and redaction; A physical approval binding that includes the disclosure manifest digest; Independent postcondition verification for the submitted destination


## What it asked for

_Nothing._
