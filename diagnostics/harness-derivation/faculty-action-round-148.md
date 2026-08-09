# Harness derivation — faculty-action — round 148

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser control readiness** — As of 2026-08-08T01:31Z, Mac agent reports Accessibility and Screen Recording granted, browser extension online with 9 Safari tabs, relay reachable, and zero browser pending commands. This supersedes the older denied/offline observation for this live session.
  - evidence: GET /ops/snapshot HTTP 200 and GET /browser/status HTTP 200

## Capabilities it proposed

### "When I say “resume that,” tell me exactly what was left unfinished and continue safely from the last verified point, even after the Mac, browser, or LTE link dropped."
- **useful because:** Today a failed multi-step action leaves the owner guessing what ran and what remains. A durable checkpoint lets the worn device and Mac recover work without repeating a purchase, duplicate message, or destructive step.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** background for checkpoint summarization; realtime only for the owner’s spoken resume command
- **latency:** Under 2 seconds to announce the checkpoint; continuation may take as long as the original task.
- **cost:** ~$0.01–$0.05 per resumed task; most cost is only the short checkpoint summary, not reprocessing the whole transcript.
- **security:** Persist action names, step ids, timestamps, and hashes—not page contents or secrets. Never auto-resume a side effect with an expired approval; require the existing physical transaction latch again. Show a clear pending/paused state on the pendant.
- **missing:** durable per-step checkpoint schema shared by planner, executor, and verifier; resume endpoint that accepts checkpoint id plus fresh approval; automatic checkpoint emission on timeout, link loss, or verification mismatch

### "Keep my browser and Mac workspaces consistent: if I ask you to “make this the same everywhere,” detect mismatched tabs, drafts, and app state, then show me a repair plan and apply only the safe changes."
- **useful because:** The browser has authenticated sessions the Mac agent cannot infer from filesystem state, while Mac apps hold drafts and local files the browser cannot see. This turns split-brain state into one understandable, cited repair instead of silently editing the wrong copy.
- **path:** browser-extension → mac-vision → mac-planner → relay → pendant → dashboard
- **model tier:** background model for diff and repair-plan generation; realtime model only for clarification and final confirmation
- **latency:** 5 seconds for a cross-surface diff; each repair step can run asynchronously with spoken progress.
- **cost:** ~$0.03–$0.15 per reconciliation, dominated by browser/page inspection; hashes and structured fields keep context small.
- **security:** Read only the explicitly named open tabs/apps. Redact secrets and message bodies by default. Classify each repair; sending, deleting, buying, or overwriting requires confirmation and fresh physical approval. Record before/after provenance.
- **missing:** common state fingerprints for browser fields, URLs, drafts, and local app records; diff/repair planner that can express no-op, safe, and approval-required changes; per-surface capability and consent scoping for the currently open Safari tabs

### "Before you send, buy, delete, or publish anything, let me hear a faithful counterfactual: what the recipient/customer/system would receive, what would change, and what cannot be undone; then let me approve that exact rendered result from the pendant."
- **useful because:** A yes/no approval is not enough when the dangerous part is misunderstanding the final rendered state. This gives the owner a chance to catch the wrong account, attachment, quantity, audience, or deletion scope without exposing secrets to the pendant or making a reversible action look safe.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** background model renders and checks the counterfactual; realtime model only narrates the short preview and handles spoken corrections
- **latency:** 3–8 seconds for a preview; approval remains valid only for a short, explicit expiry window
- **cost:** ~$0.03–$0.20 per risky action, dominated by rendering the browser/app result and one concise spoken summary
- **security:** The pendant receives only a redacted spoken summary and a digest, never credentials or full page contents. The executor must not mutate during preview. Approval binds to the exact digest, target, and parameters; any change invalidates it. Purchases, messages, deletion, and publication remain confirmation-required.
- **missing:** a non-mutating preview adapter for each action type that can render the post-action artifact; canonical digest of rendered result plus target and parameters; diff narration that identifies omissions and irreversible effects; executor gate rejecting approval when the live state differs from the preview


## Changes it proposed to its own stack

### `relay` — Add a USB-tethered pendant gateway mode: the Mac bridge owns the nRF9160 serial link when present, advertises a local relay session, forwards live button/audio/events, and drains only the existing typed OUTBOX/INBOX after authenticated acknowledgements. When USB disappears, it hands back to LTE without duplicating items; when LTE is absent, the owner still gets a local conversation through the Mac.
- **owner gets:** The pendant and ESP32 are physically connected to this Mac now, while LTE registration is not. The owner can use the wearable today at a desk and keep the same conversation and pending actions when they walk away, instead of the pendant appearing dead until cellular works.
- effort: Medium-high: serial framing/authentication, bridge session lease, transport failover, and integration tests with unplug/replug and duplicate delivery.  ·  risk: A stale USB session could accept events twice or leave the pendant believing it is online. Use monotonic session epochs, authenticated acknowledgements, and replay-safe ids; recover by dropping the lease and replaying only unacknowledged typed items.
- cost: Negligible API cost in tethered mode; engineering cost is the serial gateway and test harness. No new hardware required.  ·  latency: USB path should reduce button-to-response latency to roughly local-agent round-trip; failover adds one reconnect interval.
- security: USB is a privileged local transport: pair the bridge with a device key and bind sessions to the Mac agent bearer identity; never expose the serial port over LAN.
- depends on: serial framing for nRF9160 and ESP32 devices; transport-neutral relay session protocol; integration with existing typed OUTBOX/INBOX rather than a second spool; replay-safe event ids and session epochs


## What it asked for

_Nothing._
## Its own summary

Recorded three non-duplicate proposals: verified interruption-resume checkpoints, browser/Mac cross-surface reconciliation, and a USB-tethered pendant gateway with transport failover. Fresh probes show the Mac agent and Safari bridge are fully ready now (Accessibility and Screen Recording granted, 9 tabs online, relay reachable, no pending browser commands), contradicting older stale denial observations. I notified perception, planner, and realtime agents.

**Biggest unknown:** Whether the physically connected nRF9160/ESP32 serial devices are actually enumerated by the live Mac bridge, and the authenticated serial framing/session protocol needed to implement tether mode. I still need a concrete read-only serial/J-Link/device diagnostic surface; no such resolved tool is available yet. Owner action-policy defaults also remain unspecified, so risky resume/reconciliation steps must stay staged.

