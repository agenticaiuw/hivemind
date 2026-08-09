# Harness derivation — mac-terminal — round 247

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live USB diagnostic capability** — The granted mac_usb_serial_diagnostics schema is still unresolved in the live inventory; the call performed no serial read. Resolver's nearest match was action:get_mac_status (0.226).
  - evidence: functions.mac_usb_serial_diagnostics returned unresolved; inventory published 223 routes/109 actions and no serial capability.

## Capabilities it proposed

### "“Do that, then tell me whether it actually worked.”"
- **useful because:** This would be the system's most valuable behavior: the pendant captures the request, the Mac or authenticated browser performs it, and a second read-only observation verifies the resulting state before the answer is spoken. It prevents confident success claims when a click, script, or network action silently failed.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → unified
- **model tier:** Use realtime only for the short spoken request and final result; use a cheaper background planner for action decomposition and a deterministic verifier for known state checks. Escalate to the expensive model only when the observed state conflicts with the expected state.
- **latency:** Acknowledge on the pendant in under 500 ms; execute within the normal job budget; speak verified success or a precise unverified/failure result within 3 s after completion.
- **cost:** Typically one small planning call plus deterministic checks; roughly $0.01–$0.05 depending on whether vision or browser reasoning is needed. Verification is cheaper than re-running a failed mutation.
- **security:** The verifier must not claim success from the action receipt alone. It should retain before/after observations, URL/app identity, and a compact evidence digest, while excluding secrets and page contents. Mutations remain under the owner's existing maximum-access policy; confirmation is not introduced.
- **missing:** A first-class expected-postcondition schema attached to each action plan; Deterministic Mac/browser verifiers for common outcomes (file exists and hash, focused app state, page field/value, volume/brightness); A spoken result contract with states verified, failed, and unable_to_verify; A join between the job record, action ledger, and verification evidence

### "“Run the pendant-and-audio-bridge bench check and tell me what is unhealthy.”"
- **useful because:** The chips are physically attached today, but there is no truthful one-command health report. This would turn the current USB setup into a useful daily development instrument: enumerate both boards, run the existing dual-UART captures, validate framed counters and timestamps, exercise the audio path, and send a concise pass/fail result to the pendant without opening a microphone.
- **path:** pendant → mac-planner → mac-vision → relay-realtime → unified
- **model tier:** Use a deterministic background runner and parser; use realtime only to interpret an unusual failure for the owner. No vision or expensive reasoning is needed for normal runs.
- **latency:** Start acknowledgement under 500 ms; a 5–15 s bench run is acceptable, with a streamed progress state and a final spoken result.
- **cost:** Near-zero model cost for a normal run; one short model call only for diagnosis. Main cost is implementation of a bounded serial reader and test fixture.
- **security:** Read-only diagnostics only: fixed device paths, fixed baud/framing, bounded bytes and duration, no arbitrary shell arguments exposed in the user-facing command. USB output can contain identifiers, so retain only summarized counters and hashes unless the owner explicitly asks for logs.
- **missing:** A real host serial implementation (the granted schema is unresolved because no serial capability exists in the inventory); A parser for nRF9160 and ESP32 health/counter frames; A deterministic audio loopback or packet-loss test fixture; A Mac action that runs diagnostics/start_dual_capture.sh or dual_chip_autocapture.sh with bounded lifecycle and captures exit status; A relay-to-pendant result message for bench-only USB sessions

### "“Mark that as a decision: remember what we chose, why, and what I need to do next.”"
- **useful because:** A spoken decision should become durable, searchable context instead of disappearing into a transcript. The pendant supplies the moment and voice; the relay normalizes it; the Mac records a compact decision with the active project and current browser evidence, then optionally creates the next-action reminder. Weeks later the owner can ask what was decided and get the rationale and source, not a vague summary.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime extracts only the explicit decision, rationale, and next action. A cheaper background model links entities and deduplicates against the context graph; deterministic code writes the record and reminder.
- **latency:** Acknowledge capture immediately; save the decision within 2 s; reminder creation may complete asynchronously with a spoken receipt.
- **cost:** About $0.005–$0.03 per decision, dominated by transcription/context extraction. Browser provenance and graph writes are local/low cost.
- **security:** Store only the owner's explicit decision and a short rationale, not a full audio transcript or page dump. Attach source URLs and provenance IDs, redact credentials, and distinguish quoted evidence from model inference. Creating a reminder should be reported as a separate side effect.
- **missing:** A typed decision record with fields decision, rationale, alternatives, owner, project, next_action, due_at, confidence, and evidence_refs; A context-graph query that finds prior decisions and detects contradictions; A compact spoken capture protocol from the pendant to the relay; A provenance-aware answer route that can cite browser evidence without exposing page secrets

### "“Approve this sign-in.”"
- **useful because:** The owner should be able to authenticate to a browser session without exposing a password or leaving the keyboard to find a phone. The browser extension presents the challenge, the relay binds it to the intended origin, and the pendant's physical button plus a spoken origin/read-back authorizes exactly that one ceremony. This makes the worn device a practical hardware-backed approval surface rather than merely a microphone.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → unified
- **model tier:** Deterministic challenge binding and origin checking do the security-critical work; realtime handles only the short spoken read-back and confirmation phrase. No background model is needed for normal approval.
- **latency:** Challenge display and pendant prompt under 1 s; approval completion under 5 s, with an explicit timeout and no retry ambiguity.
- **cost:** Near-zero per approval after implementation; one short realtime turn when speech read-back is used. Engineering cost is dominated by WebAuthn/passkey integration and secure pendant key storage.
- **security:** The relay must never receive a password or reusable bearer token. Bind the signed response to origin, tab/session, challenge, expiry, and a monotonic pendant counter; refuse if the browser tab changes. Require the physical button edge and truthful local status, and retain only a non-secret audit receipt.
- **missing:** A secure private-key or passkey slot on the pendant (or a companion secure element); A browser-extension WebAuthn bridge that can bind challenges to tab origin and session; A relay route for challenge registration, expiry, replay protection, and signed response delivery; A spoken origin-normalization policy that does not read lookalike domains ambiguously

### "“Why are you telling me this, and what exactly did you use?”"
- **useful because:** Today the system can produce answers from several bodies, but the owner cannot ask for a compact, end-to-end explanation of which pendant utterance, Mac state, browser page, and model inference led to it. This capability would return a human-sized evidence chain, separating observed facts from guesses and showing what was omitted or stale. It is especially valuable when the owner is moving quickly and cannot inspect a dashboard.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → unified
- **model tier:** Deterministic provenance collection and freshness checks first; a cheap summarizer turns the chain into speech. Use the expensive realtime tier only when the owner asks a nuanced follow-up about conflicting evidence.
- **latency:** Answer a simple 'why' in under 2 s from stored receipts; a multi-source reconstruction may take 5 s and should announce that it is assembling evidence.
- **cost:** Usually under $0.01 because evidence is already local and summarization is small; cost rises only for conflict resolution across many sources.
- **security:** Speak source labels and minimal excerpts, never secrets or full authenticated page contents. Mark model-derived claims as inference, preserve source timestamps and freshness, and allow the owner to erase the evidence capsule with the underlying job.
- **missing:** A unified evidence-capsule format spanning voice turns, Mac observations, browser provenance, and model claims; Stable correlation IDs propagated through relay, browser, and Mac jobs; Freshness and contradiction evaluation before speech; A compact pendant audio response format for 'observed', 'inferred', and 'not checked'

### "“Keep this private, but make it available on my Mac and in my browser when I need it.”"
- **useful because:** The owner should be able to create a genuinely private personal note from the pendant and later retrieve it across the Mac and an authenticated browser session without sending plaintext to the relay or model provider. The pendant encrypts the utterance locally, the relay transports ciphertext, and the Mac/browser decrypt only after local-device authentication. This is a capability ordinary assistants cannot provide because they do not span the worn key, relay, host, and browser session.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Realtime performs only local intent detection and an optional acknowledgement; encryption, storage, access control, and browser insertion are deterministic. A background model may index locally encrypted metadata, but never receives plaintext unless the owner explicitly unlocks it.
- **latency:** Capture acknowledgement under 500 ms; encrypted persistence within 2 s; local retrieval and insertion under 1 s after unlock.
- **cost:** Negligible per note. Hardware work is the major cost if a secure element is required; storage and relay bandwidth are tiny.
- **security:** Use per-note envelope encryption, hardware-bound keys, expiry/revocation, and explicit origin binding before browser insertion. The relay stores ciphertext only. Avoid searchable plaintext metadata; if local search is needed, use an encrypted index and accept slower unlock-time search. A lost pendant must be revocable from the Mac.
- **missing:** A pendant secure-element/key-management design and local encryption primitive; A relay ciphertext-only mailbox with replay protection and deletion semantics; A Mac key broker gated by local device presence, with recovery and revocation; A browser-extension API that inserts decrypted text only into the explicitly selected origin/tab; A user-facing recovery path that does not turn the relay into a plaintext escrow


## Changes it proposed to its own stack

### `mac-harness` — Add a bounded, typed bench-session runner that is separate from general run_shell: it selects only the two known USB ports, starts the existing dual-chip capture scripts, records child PID/exit code/stdout-stderr tails and frame counters, kills the process group on timeout, and emits one durable bench-session artifact linked to the originating job. This is observability and recovery, not an approval gate or a narrower general shell policy.
- **owner gets:** The owner can plug in the pendant and bridge and receive an honest diagnosis instead of a command that may hang, overflow, orphan, or report success without proving either board answered.
- effort: Medium: host serial framing, process-group lifecycle, parser fixtures, and a small route/action wrapper.  ·  risk: A malformed frame or unplugged board could terminate a session early; report partial results explicitly and preserve bounded raw tails for debugging. Never let a bench session touch arbitrary files or the network.
- cost: Negligible API cost; modest engineering time and a few kilobytes per run for summarized evidence.  ·  latency: No impact on ordinary Mac actions. Bench runs become bounded and cancellable rather than inheriting the 120-second shell timeout.
- security: Improves auditability without changing the owner's maximum-access policy; fixed ports and redacted output prevent accidental token/log leakage from the diagnostic path.
- depends on: A real serial capability or a narrowly implemented local-agent adapter (the currently granted mac_usb_serial_diagnostics remains unresolved); The existing diagnostics/start_dual_capture.sh and dual_chip_autocapture.sh scripts; A typed bench result schema consumed by the pendant status beacon

### `hardware` — Add a small secure element to the next pendant revision, with a non-exportable device key, monotonic counter, and physical-button-gated signing operation; keep the nRF9160 as the transport and audio controller. Pair it with a Mac-side revocation record and relay ciphertext mailbox rather than putting secrets in firmware flash.
- **owner gets:** The pendant could safely approve a browser sign-in and unlock private notes without passwords or reusable secrets ever passing through the relay, making it trustworthy as the owner's always-present identity token.
- effort: Medium hardware and firmware integration: secure-element layout, provisioning, recovery/revocation UX, and signed-message protocol.  ·  risk: Lost or damaged pendant could strand access if recovery is weak; provide a second-device recovery ceremony and revocation, and never silently fall back to an unprotected key. Added signing latency must not interfere with the active microphone edge.
- cost: Roughly a few dollars per unit and tens of milliwatts only during signing; board spin and provisioning are the meaningful costs.  ·  latency: Typically tens of milliseconds per signature, outside the audio hot path.
- security: Strongly improves key isolation and origin-bound approvals; introduces provisioning and recovery secrets that must be handled offline and audited.
- depends on: A defined origin-bound browser approval protocol; Ciphertext-only relay mailbox and Mac key broker; Pendant firmware support for button-gated secure-element signing; A recovery and revocation flow across Mac and relay


## What it asked for

_Nothing._
## Its own summary

Produced three owner-facing capabilities and one stack change. The strongest is verified action outcome: execute through Mac/browser, then independently observe the resulting state and speak verified/failed/unable-to-verify rather than trusting receipts. I also specified a decision-capture workflow spanning pendant, relay, browser provenance, project context, and reminders, plus a bounded USB bench-session runner for the physically attached chips. Live discovery confirmed Safari is online, the Mac bridge is online, and the granted serial-diagnostics schema still has no implementation; its call did not touch either port.

**Biggest unknown:** Whether the relay currently exposes a usable wearable-to-Mac event/audio handoff beyond the known pipeline routes. I asked relay-realtime. The concrete work still needed is a real serial adapter/parser, typed postconditions and verifiers, and a durable decision record with contradiction lookup.

