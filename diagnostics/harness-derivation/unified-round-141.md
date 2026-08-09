# Harness derivation — unified — round 141

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Is my pendant actually ready right now? Test the complete local conversation path and tell me what will fail before I rely on it.”"
- **useful because:** The owner currently has to know which fixture, serial link, bridge, and validator to invoke. A single explicit readiness check would exercise the physically connected nRF9160 and ESP32 over USB, run a bounded synthetic uplink/downlink turn, correlate bridge acknowledgements with relay/pipeline receipts, and return a plain HEALTHY/DEGRADED/BLOCKED verdict plus the exact failing hop. This is materially different from a periodic diagnostic fixture: it is an owner-invoked pre-use gate on the live USB session, not a background test.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** deterministic for capture/measurement and verdict; realtime only to explain an anomalous result conversationally
- **latency:** 15–30 seconds for the bounded fixture; never run on the hot path of a real conversation
- **cost:** <$0.01 per invocation; dominated by one short fixture turn and any optional realtime explanation
- **security:** Synthetic audio only, no microphone content or page data; require a physical start press or explicit owner request, redact serial identifiers in spoken output, and retain only counters/receipt IDs
- **missing:** A safe Mac USB-serial session runner that can invoke the existing firmware self-test without arbitrary shell; A typed correlation endpoint joining serial frame ACKs, pipeline artifacts, and audio_delivery_ack_queue records; A dashboard/voice presentation for the verdict and remediation link

### "“What information left my devices today, where did it go, and what is still queued to leave?”"
- **useful because:** Privacy is currently a latch and a convergence check, but the owner has no retrospective, human-readable accounting of actual egress. This would merge relay job payload classes, browser command targets, Mac job receipts, audio artifact metadata, and pendant outbox/inbox state into a time-bounded report with explicit unknowns. It lets the owner detect an unexpected destination without exposing secrets or requiring them to inspect five logs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background deterministic aggregation; cheap model only for labeling and summarizing already-redacted records
- **latency:** Under 5 seconds for a 24-hour report; stream progress if the owner asks for a longer interval
- **cost:** <$0.01; aggregation dominates, model use is optional
- **security:** This report is itself sensitive. Do not include raw audio, page contents, tokens, message bodies, or form values; show destination domains/app names, data class, byte/count totals, timestamps, retention/queue state, and confidence. Require explicit owner request and make the report local-only by default.
- **missing:** A tamper-evident egress event envelope emitted by every relay/Mac/browser/pendant transport; A read-only join route with a strict redaction schema and retention window; Pendant OUTBOX/INBOX status exposure over the current USB fallback session

### "“Continue that conversation on whichever link is working, without making me repeat myself or hearing a duplicate reply.”"
- **useful because:** The pendant is physically testable over USB today while LTE is unregistered, and the system already has multiple transport bodies. A turn-boundary handoff would carry only a signed conversation/turn cursor and a compact semantic state, pause the old speaker, resume capture on the new link, and suppress duplicate audio by artifact ID. The owner experiences one continuous assistant despite modem loss, Mac sleep/wake, or bridge replacement.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** deterministic state machine and deduplication; background model only to compress approved conversation state when it exceeds the cursor budget
- **latency:** Handoff at the next turn boundary, target under 2 seconds; never switch mid-audio frame
- **cost:** <$0.01 per handoff; dominated by a small state envelope, not generated audio
- **security:** Never persist raw microphone/audio merely to hand off. Bind state to a session nonce, monotonic turn counter, and authenticated transport; expire abandoned cursors; make the owner’s privacy latch suppress both capture and migration. Browser state must remain tab-bound and never be copied into the pendant.
- **missing:** A relay-owned transport session record with an atomic active-owner lease and turn cursor; USB↔LTE handoff signaling in firmware/bridge, including explicit old-owner stop receipt; Audio artifact deduplication across the relay and bridge, plus a bounded semantic-state schema; A policy for whether a handoff may occur while an approval or irreversible action is pending

### "“Why did you do that, what evidence did you rely on, and what exactly changed in the world?”"
- **useful because:** Today the system can expose separate jobs, receipts, browser results, and evidence candidates, but the owner cannot obtain one causal, read-only reconstruction of a decision. This capability would connect the spoken request to the model plan, policy classification, approvals or physical consent, concrete Mac/browser mutations, post-state observations, and any undo or failure. It would explicitly distinguish observed facts from inferred explanations and say when provenance is missing. That is the difference between an audit trail the owner can trust and a pile of logs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic provenance assembly first; a background model may summarize the assembled graph, but must not invent missing links
- **latency:** Under 5 seconds for a recent action; up to 20 seconds for a multi-step historical reconstruction
- **cost:** <$0.02 per reconstruction; storage/index joins dominate, with optional summarization as the only model cost
- **security:** Read-only and least-privilege. Redact tokens, page contents, private message bodies, and microphone audio. Bind queries to the owner’s job/session and show provenance gaps instead of silently broadening access. Any suggested remediation must be separate from the explanation and require its normal confirmation.
- **missing:** A durable causal-link schema connecting request, plan, policy decision, approval, action, receipt, observation, and undo; Immutable post-state fingerprints for browser and Mac actions where safe to collect; A typed read-only provenance query and dashboard/talker rendering with confidence and missing-evidence states

### "“For this task, let yourself prepare everything, but never send, purchase, delete, or publish without asking me.”"
- **useful because:** The current action system classifies individual actions, but the owner cannot issue a temporary, human-readable delegation contract that constrains an entire multi-step task across Mac and browser surfaces. This would compile the owner’s limits into a signed, expiring session policy, stop execution before a disallowed step, and report what was prepared versus what remains blocked. It gives the owner useful autonomy without turning every safe intermediate action into a separate interruption.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic policy compilation and enforcement; planner model may propose steps but cannot weaken the contract
- **latency:** Policy check under 100 ms per action; owner-facing explanation under 2 seconds
- **cost:** <$0.01 per task; policy checks are local, with model cost only for planning or explanation
- **security:** Fail closed on missing or ambiguous policy. Bind the contract to session, surface, target, action types, and expiry; do not accept natural-language reinterpretation after approval. Keep secrets and page content out of the relay policy record. Require the existing physical transaction approval for any action outside the contract.
- **missing:** A first-class task-scoped policy token enforced by both Mac and browser executors; A deny-before-dispatch hook shared by /execute and browser commands; An owner-facing contract preview and explicit expiry/revocation path

### "“Before you change anything, show me the exact world-diff you expect, including files, browser records, messages, and settings, then let me approve only that diff.”"
- **useful because:** Existing previews are feature-specific and can miss cross-surface effects. A general preflight would produce a typed expected-world diff for a multi-step plan, identify irreversible or unobservable effects, and bind any approval to the diff so a changed plan or moved world is refused. The owner gets a concrete answer to ‘what will happen?’ rather than trusting a prose promise.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic diff and binding engine; planner model only translates the owner’s intent into candidate actions
- **latency:** 2–5 seconds for a normal plan; longer only for explicit multi-app scans
- **cost:** <$0.02; filesystem/browser state inspection dominates, with optional natural-language rendering
- **security:** Default to metadata and hashes, not contents. Never read unrelated tabs or files to construct a diff. Mark effects that cannot be predicted, such as external service-side changes, and require stronger confirmation rather than pretending they are known.
- **missing:** A common expected-world-diff schema for Mac files/settings, browser state, and external side effects; Dry-run adapters for every executor action, with explicit unknown-effect results; A cryptographically bound approval record and a renderer usable over the pendant


## Changes it proposed to its own stack

### `firmware` — Add a bounded, sequence-aware Bluetooth playback continuity layer in the ESP32 bridge: replace silence-on-gap with a short PLC/fade policy, track the SBC/A2DP clock against incoming frame timestamps, and expose underrun, concealment, and reconnect counters in the existing audio delivery receipt. Keep the buffer below the measured 44 kB failure point and make the policy disable itself when RAM watermark is unsafe.
- **owner gets:** When the Bose/A2DP link hiccups, the owner should hear a brief unobtrusive fade rather than a click, repeated phrase, or several seconds of silence, and should know whether the fault was the bridge, Bluetooth, or relay.
- effort: Medium: bridge firmware state machine, timestamp plumbing, and hardware tests across reconnect/gap profiles.  ·  risk: A bad clock correction could stretch speech or conceal real content. Bound concealment to a few frames, emit a degraded receipt, and fall back to current hard mute on repeated gaps; validate with synthetic fixtures before enabling by default.
- cost: No API cost; roughly 2–6 KB RAM for metadata and a small PCM concealment window, plus negligible flash. Must stay well below the known 44 kB buffer starvation threshold.  ·  latency: Adds no steady-state latency; at most one short concealment window during a gap.
- security: No new content storage or network destination; counters are metadata only and should inherit existing delivery-receipt redaction.
- depends on: audio_delivery_ack_queue; audio_path_diagnostic_fixture; A typed bridge frame-ack/counter path over the existing USB serial link


## What it asked for

_Nothing._
