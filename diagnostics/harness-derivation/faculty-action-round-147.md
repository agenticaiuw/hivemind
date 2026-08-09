# Harness derivation — faculty-action — round 147

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live action preflight** — Mac bridge is online and ready; Accessibility, Screen Recording, and all listed automation permissions are granted to com.aipendant.agent. Safari browser extension is online with 9 tabs and no pending commands. Relay is reachable, but no nRF pendant is registered; the currently testable worn-device path is USB-attached hardware if the serial harness is used.
  - evidence: GET /ops/status at 2026-08-08T01:25:14Z returned agent.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser.online=true, pendingCommands=0, relay.reachable=true; GET /devices reported only Mac bridge, Safari, and offline mobile.

## Capabilities it proposed

### "“Pause interruptions for the next hour, but remember exactly what was already enabled so you can put it back.” The pendant should let me start and cancel this without opening a screen."
- **useful because:** A wearable should be able to create a reversible quiet bubble across every surface, not merely mute one app. The Mac changes Focus/notification state, the browser suppresses extension prompts, and the relay keeps the deadline and restores the prior state even if the pendant disconnects. A single deliberate pendant gesture can confirm the state-changing transaction; the owner gets a spoken confirmation without exposing private notification contents.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-action
- **model tier:** Use realtime only to interpret the short voice request; use a cheap background relay job for deadline monitoring and restoration. Mac/browser actions are deterministic; faculty-perception independently verifies each changed state.
- **latency:** Start acknowledgement under 2 seconds; apply changes within 5 seconds; restoration is deadline-triggered and should complete within 10 seconds of expiry or reconnect.
- **cost:** Usually one short realtime turn plus deterministic Mac/extension calls; roughly $0.01–$0.04 per invocation, dominated by realtime audio, with no model calls during the quiet interval.
- **security:** The relay must store only an opaque transaction and hashed pre-state, not notification text. Changing Focus is reversible but affects communications, so require the existing physical transaction approval latch unless the owner explicitly configures this action class as proactive. If restoration cannot be verified, leave the system unchanged and report unknown rather than claiming success.
- **missing:** A cross-surface Focus/notification adapter that snapshots and restores prior state; A durable deadline runner that survives relay/Mac restarts; A browser command to suspend only Pendant-originated prompts; A policy entry for whether quiet bubbles need physical approval

### "“I’m moving from my Mac to just the pendant. Continue the task when I reconnect, but never repeat a step that already happened.”"
- **useful because:** Today a dropped link turns a real-world workflow into an ambiguous partial failure. This gives the owner a durable handoff: the relay checkpoints each action, the Mac/browser report signed receipts, and faculty-perception rechecks postconditions after reconnect before faculty-action resumes. It is especially useful for long tasks such as filing, booking, or multi-page forms where repeating a click can duplicate an order or message.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-action → faculty-perception
- **model tier:** Realtime handles only the owner's handoff/cancel utterance. A background durable worker runs the checkpoint state machine; no LLM is needed for retries, and perception is invoked only for a disputed or stale checkpoint.
- **latency:** Checkpoint receipt under 1 second after each action; reconnect reconciliation under 5 seconds; resume only after fresh verification, otherwise surface a concise pending decision to the pendant.
- **cost:** Near-zero model cost for ordinary runs; storage and verification dominate. A complex ambiguous recovery might use one background planner call, under $0.02 typical.
- **security:** Never replay an action from intent text alone. Bind checkpoints to session, tab, action digest, and expiry; redact form secrets from receipts. Any irreversible step whose postcondition is unknown must stop and require the existing physical approval latch, not auto-retry.
- **missing:** Durable cross-surface execution/checkpoint protocol with idempotency keys; Executor receipts that include action and target digests without secrets; Reconnect reconciliation worker and UI/voice status vocabulary; A resume policy integrated with existing actionRisk/policyRouter

### "“Read me the exact thing I’m about to send, then let me approve it with the pendant—without putting the private draft on the pendant.”"
- **useful because:** This is the safest practical bridge between voice and authenticated browser/Mac sessions: the owner can dictate or edit a message, hear a short local confirmation derived from the actual draft, and approve the exact digest physically. The browser or Mail session retains the secret/body; the pendant receives only a redacted spoken preview and an opaque digest. The action agent submits only after fresh verification that the draft still matches what was approved.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Realtime transcribes the owner’s short command and reads a concise preview; deterministic code computes the canonical draft digest. Background verification checks the draft immediately before submission; no expensive model is needed unless the owner asks for rewriting.
- **latency:** Draft preview within 3 seconds; approval-to-submit within 2 seconds; if the draft changes or the browser session disappears, stop and ask again.
- **cost:** About $0.01–$0.03 per message, mostly realtime audio; hashing, browser verification, and submission are deterministic.
- **security:** Do not send message bodies, credentials, or browser screenshots to the pendant or relay logs. Speak only an owner-selected limited preview (for example recipient and first 80 characters) and show the full draft on the already-authenticated Mac if needed. Approval envelope must bind recipient, channel, canonical body hash, attachments hash, expiry, and action risk. A mismatch, stale tab, or uncertain postcondition is a hard stop.
- **missing:** Canonical draft extraction and stable hashing for Mail and browser compose surfaces; A privacy-preserving spoken preview/redaction policy; Pre-submit verifier that checks recipient/body/attachments against the approval digest; A single submit adapter with truthful sent/unknown result reporting

### "“Only let actions I have explicitly approved continue while I’m wearing the pendant; if it leaves me, freeze everything sensitive immediately.”"
- **useful because:** The pendant can become a physical presence key for the whole agent, not merely a button for individual approvals. Losing the pendant, disconnecting it, or walking away from the Mac would revoke execution leases for sensitive browser and Mac actions before a queued command can submit. This protects authenticated sessions when the owner is not at the machine.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-action → faculty-perception
- **model tier:** No model is needed for enforcement. A background lease monitor handles presence and revocation; realtime is used only to explain a pause or request a new approval.
- **latency:** Revoke sensitive leases within 2 seconds of presence loss; resume only after a fresh physical gesture and current-state verification.
- **cost:** Negligible model cost; small relay state and heartbeat traffic. Occasional explanatory voice response may cost under $0.01.
- **security:** Presence must not be inferred from a stale relay heartbeat. Use signed monotonic presence epochs and short leases; fail closed on clock ambiguity or duplicate devices. Never expose secrets to the pendant. Non-sensitive read-only work may continue only under an owner-configured policy.
- **missing:** A hardware-backed or signed pendant presence heartbeat usable over USB today and LTE later; Sensitive-action lease enforcement in policyRouter and browser command execution; Immediate revocation hooks for queued Mac jobs and browser commands; Owner-configurable classification of sensitive versus harmless actions

### "“Let the agent work with my accounts without ever seeing the secrets—fill the password or payment field through a protected handle, and tell me only whether it succeeded.”"
- **useful because:** Authenticated browser sessions currently force the action layer to operate near secrets. A capability-level redaction boundary would let the agent navigate and submit forms while credentials and payment data remain in a local vault or browser-native credential provider. The owner gets a useful result and provenance without leaking values into relay logs, model context, pendant audio, screenshots, or receipts.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → faculty-action → faculty-perception
- **model tier:** Deterministic browser and vault adapters do the filling. Use a cheap background classifier only to identify unexpected secret fields; use realtime for the owner-facing result, never for credential handling.
- **latency:** Protected field fill within 2 seconds; abort immediately if the DOM field, origin, or credential target changes. Verification should return a boolean/status plus redacted provenance within 3 seconds.
- **cost:** Near-zero model cost for known origins and fields; occasional classification under $0.01. Storage and local vault integration dominate engineering, not invocation cost.
- **security:** Credential values must remain on-device, never enter page text returned to the model, and never be persisted in action receipts. Bind handles to origin, frame, field purpose, and expiry; require physical approval for payments, account changes, and submissions. A changed origin or unexpected field is a hard stop.
- **missing:** A local secret-handle API backed by the owner’s macOS credential store or browser password manager; Browser-extension content isolation that fills opaque handles without returning values; Origin/field attestation and redacted verification receipts; A policy mapping secret-field classes to mandatory physical approval

### "“At the end of the day, tell me which actions actually changed the world, which are still unknown, and let me undo only the ones that are safely reversible.”"
- **useful because:** The owner needs a truthful operational ledger rather than a list of model intentions. This capability would reconcile Mac receipts, browser state, and independent perception into a spoken, privacy-filtered action history classified as verified, failed, or unknown, then offer targeted undo only where a tested inverse exists. It makes the system trustworthy after crashes, retries, and ambiguous submissions.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action → faculty-perception → mac-terminal
- **model tier:** Use deterministic receipt aggregation and verification. A cheaper background model can compress the day’s events; realtime is reserved for the owner asking for the report or selecting an undo.
- **latency:** On request, produce a concise report within 5 seconds; each selected undo should begin within 2 seconds and receive independent verification within 10 seconds.
- **cost:** Usually under $0.01 using stored receipts and deterministic checks; background summarization is the dominant model cost and can be batched once per day.
- **security:** Logs must contain hashes and redacted summaries, not message bodies, credentials, or page contents. Never label an unverified external side effect as failed or successful. Undo requires a fresh risk check and physical approval for consequential changes; if no safe inverse exists, explain that plainly.
- **missing:** A durable cross-surface action ledger with common correlation IDs; A registry of verified inverse operations and their preconditions; Daily reconciliation and privacy-filtered summarization; A pendant query/selection protocol for choosing one ledger item to undo


## What it asked for

_Nothing._
