# Harness derivation — faculty-action — round 107

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **execution-surfaces** — Mac bridge is online and relay reachable, but browser extension home-chrome is offline with 10 pending commands; no pendant is present in device table.
  - evidence: GET /ops/status and discover(devices), 2026-08-07
- **mac-permissions** — AI Pendant Agent still lacks Accessibility and Screen Recording; AppleScript automation grants are present and requiredMissing is empty, but readiness is false.
  - evidence: GET /ops/status permissions object, 2026-08-07
- **owner-policy** — Owner permits browser reads/clicks and reminders/notes without asking; destructive mail/file/purchase actions require confirmation; timezone is America/Chicago.
  - evidence: discover(owner) remembered projection, 2026-08-07

## Capabilities it proposed

### "“Put me back exactly where I left off, and let me continue from the pendant.” The system should preserve a live handoff capsule: what I was trying to do, the relevant Mac app/document, authenticated browser tabs and page locations, selected text or draft state, and the next safe action. If the link drops, I can press the pendant button later and hear a concise resume brief; the Mac and browser restore only the reversible context, then wait for my confirmation before changing anything."
- **useful because:** Today the pendant, relay, Mac, and private browser are separate sessions. After walking away or losing connectivity, the owner must reconstruct context manually and risks acting on stale tabs or drafts. This gives them continuity across the one place they speak and the machines that hold their work, without silently submitting anything.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use a cheap background model to compress and refresh the handoff capsule; use the realtime tier only to hear the button-triggered resume brief; use the local Mac planner for deterministic restoration and a small model only when the capsule is ambiguous.
- **latency:** Capture should complete in under 2 seconds while online. Resume speech should begin within 1 second of a pendant button press; restoring reversible context may take 3–10 seconds and must report partial availability rather than blocking.
- **cost:** About $0.001–$0.02 per capture/resume depending on capsule compression and whether page text is summarized; storage and browser/Mac round trips dominate, not realtime inference.
- **security:** Capsules can contain private URLs, page text, drafts, and document names. Encrypt at rest and in transit, bind each capsule to the paired device, redact secrets and passwords, give every capsule a TTL and delete control, and never restore or mutate a private page without an explicit owner confirmation. A stale capsule must be visibly labeled with age and source.
- **missing:** A versioned handoff-capsule schema with provenance, sensitivity labels, TTL, and stale-state detection; A pendant-local offline queue and a reliable sync/replay protocol when the relay reconnects; Mac APIs to snapshot and restore reversible app/document context without Accessibility or Screen Recording; Browser bridge support for authenticated tab snapshots and reattachment, currently unavailable while home-chrome is offline; A user-facing resume/expiry/forget control and a compact spoken status path


## Changes it proposed to its own stack

### `integration` — Add a cross-surface action transaction coordinator above /plan and /execute. For every judged action bundle, create a durable transaction with an idempotency key, explicit preconditions, a short owner approval lease, and a per-step evidence requirement. Route reversible Mac steps through mac_run_actions and authenticated browser steps through the browser command queue; after each step, collect typed state evidence (job receipt, browser result, AppleScript/readback, or pipeline event), mark the step committed only when the expected state is observed, and stop/recover on mismatch. Expose one compact spoken status plus a durable journal linking transaction, step, evidence, undo token, and final outcome. This is not another receipt: it makes a multi-device action atomic-ish and prevents claiming completion after partial execution.
- **owner gets:** When the owner says “do it,” they get a trustworthy answer about what actually changed—even if the browser disconnects or the Mac disappears halfway through—and can resume or undo the exact completed parts instead of guessing.
- effort: Medium-high: coordinator state machine, adapters for Mac/browser/relay, evidence schemas, crash recovery, and dashboard/journal UI; test with injected disconnects and duplicate requests.  ·  risk: A false positive evidence matcher could mark an action complete incorrectly; a false negative could stop after a successful step. Default to stop-and-report, require explicit expected-state predicates from judgement, and retain undo/retry metadata. Never send mail, delete, purchase, or submit without the existing confirmation policy.
- cost: Negligible storage/compute overhead; one extra low-cost verification/readback per step. Realtime model is not needed except for the final spoken status.  ·  latency: Adds roughly 0.5–2 seconds per step for readback/evidence; avoids long expensive retries and duplicate actions.
- security: Journal may contain sensitive URLs and before/after values; encrypt or redact evidence, enforce per-transaction access, and expire raw page content while retaining hashes and outcome metadata.
- depends on: A durable job runner and browser queue with request IDs/tab affinity (chg-16bc5dee and chg-14accc01); Approval gates/action leases and verification tools currently requested but not yet present; Mac and browser surfaces becoming reachable; currently home-macbook-bridge is online but home-chrome is offline; Owner-defined expected-state predicates for high-impact actions


## What it asked for

_Nothing._
## Its own summary

Discovered the live action surfaces and recorded a new integration change: a cross-surface action transaction coordinator with idempotency, approval lease, per-step expected-state evidence, stop/recovery on mismatch, and durable undo-linked journal. Mac bridge and relay are reachable; browser and pendant are not.

**Biggest unknown:** The exact owner-approved expected-state predicates and confirmation/lease/verification contracts for consequential actions are still undefined; peer answers may clarify them next round.

