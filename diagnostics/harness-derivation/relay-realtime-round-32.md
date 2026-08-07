# Harness derivation — relay-realtime — round 32

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on long tasks after I stop talking, and tell me what happened when it finishes."
- **useful because:** This fits the pendant: the owner can start something while walking, then get a clear completion receipt later without staying in a live conversation.
- **path:** pendant → relay → mac-bridge → browser → relay
- **model tier:** Cheaper background planner for the task; realtime only for brief status updates.
- **latency:** Start quickly (under a second to acknowledge) and finish asynchronously; completion delivery can be seconds to minutes later.
- **cost:** Low per invocation; main cost is background planning/execution on the Mac and any browser interactions, plus storing status receipts.
- **security:** Must not claim success without a verified completion record. Must treat private pages and accounts as sensitive; drafts and changes should be staged and confirmed where appropriate.
- **missing:** No scheduler/queue for deferred work and status delivery across surfaces; Unified receipt channel (push to pendant, plus a Mac/browser review queue); Reliable cross-surface job IDs and idempotency for retries

### "“Prep me for my next meeting.” Then, wherever I am, tell me who it is with, the relevant history and open decisions from my Mac, and any authenticated browser workspace, and give me a 60-second spoken brief; leave a resumable source-linked packet on my Mac so I can continue later."
- **useful because:** Today no single node can combine the owner’s calendar/mail/files and browser sessions into one trustworthy, source-linked briefing while the owner is away from the Mac. This turns an underspecified spoken request into immediate situational awareness without making the owner hunt through apps.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use relay-realtime only to capture the request, resolve the next-meeting target, and speak the final brief. Use a cheaper background model for extraction, deduplication, and synthesis after mac-planner and browser return evidence; use mac-planner for local Calendar/Mail/files and browser for authenticated web workspaces.
- **latency:** Acknowledge on the pendant in under 1 second; return a first spoken brief within 20–40 seconds, with progressive updates if either Mac or browser evidence is slow. Packet assembly can continue after the first brief.
- **cost:** Roughly $0.03–$0.20 per invocation depending on document volume; model synthesis and repeated context are the dominant costs, while browser/Mac extraction is comparatively cheap.
- **security:** Potentially sensitive meeting, mail, file, and authenticated-web data leaves those surfaces and is sent to the synthesis model. Keep raw sources on their originating surfaces where possible, send extracted snippets plus provenance, encrypt the packet, and clearly identify which claims came from which source. Reading is reversible and should not require confirmation; saving a local packet is reversible. Never send mail, edit shared documents, or expose browser contents externally as part of this capability without an explicit follow-up command.
- **missing:** A cross-surface orchestrator that can select the next meeting and launch parallel Mac and authenticated-browser evidence collection; A common evidence schema with source URLs/file paths, timestamps, permissions, and confidence so synthesis can cite rather than hallucinate; A resumable job/packet store and a pendant-friendly progressive result channel; A Mac-side packet renderer and browser extractor that can return bounded, relevant content instead of entire sessions

### "“Is the project build broken, and if so fix what you safely can?” From the pendant, inspect the current repository and local test/build state on my Mac, correlate it with the authenticated CI/issue tracker in my browser, explain the likely root cause in plain speech, and optionally apply a reversible fix and report the exact diff and verification result."
- **useful because:** A wearable request could answer the question that currently requires manually checking several disconnected surfaces: local source and logs, CI status, and issue context. It is valuable while the Mac is unattended because the relay can collect evidence, have the Mac planner/terminal perform bounded diagnosis, and use the browser session for private CI details that the server cannot access.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Relay-realtime should only classify the request and speak progress. mac-terminal/mac-planner should run deterministic tests and inspect diffs; browser should retrieve authenticated CI and issue evidence; a cheaper background reasoning model should correlate logs and propose a patch. Reserve realtime for the final conversational explanation or a follow-up question.
- **latency:** Acknowledge immediately, provide an initial health result in 10–20 seconds, and provide diagnosis within 60 seconds. A patch may take several minutes; stream milestones and make the final spoken answer independent of the pendant remaining connected.
- **cost:** Approximately $0.05–$0.40 per run, dominated by log/context ingestion and patch reasoning; deterministic command execution and browser extraction are low cost.
- **security:** Source code, private logs, issue text, and CI credentials/session-derived content are sensitive. Send bounded excerpts and metadata rather than whole repositories; redact secrets before model calls; never expose browser cookies or tokens. Read-only diagnosis can run without confirmation under the owner’s policy. Applying a patch must be constrained to a worktree or reversible commit, must not push, merge, delete, or alter production, and should produce a receipt plus rollback command.
- **missing:** A cross-surface job coordinator that joins local repository identity with the correct authenticated CI/project in the browser; A secret-redacting log and diff collector with hard output limits; A sandboxed worktree/rollback execution mode for mac-terminal, plus verification receipts; A progress stream and durable result record that the relay can summarize after a dropped LTE connection


## Changes it proposed to its own stack

### `integration` — Add a small, durable job orchestration layer with idempotency keys, retries, and completion receipts stored in a shared job log. Use the relay as the front door, the Mac/browser as workers, and a receipt fan-out to pendant voice notifications and a review queue on the Mac.
- **owner gets:** They can hand off a task, walk away, and later hear exactly what finished, failed, or needs approval — without babysitting it.
- effort: Medium to high: requires shared persistence, worker coordination, and receipt delivery plumbing.  ·  risk: Duplicate execution if idempotency is wrong; mitigated by idempotency keys and typed job states. Partial failures must be resumable and auditable.
- cost: Moderate: storage for job metadata and receipts; compute for retries. Worth it because it avoids keeping the expensive realtime tier busy.  ·  latency: Improves perceived latency: quick acknowledgement now, work continues in cheaper tiers.
- security: Job logs contain sensitive task context; needs access controls, redaction, and retention controls.
- depends on: A durable storage mechanism for jobs/receipts (D1 or Durable Objects); A notification path to the pendant (push or poll)


## What it asked for

### `c12-4hc1` (context) — What the granted tool list means when names appear in the 'granted' category but are not describable via describe(name).
- why: I discovered entries like relay_route_intent and server_browser_actions in the 'granted' list, but describe() says they do not exist. I need to know whether these are conceptual grants, different names, or missing registrations.
- would change: If they exist under different names, I will call those. If they are not registered as tools, I will stop trying to use them and instead request the correct tool or use existing routing tools (mac_delegate, mac_run_actions, browser_run_actions) as the contract requires.

## Its own summary

Recorded two new capabilities: a cross-surface “prep me for my next meeting” briefing that joins local Mac data with authenticated browser workspaces and produces a source-linked packet plus spoken brief; and remote build/CI diagnosis and safe reversible repair from the pendant, correlating local repository state with private browser CI/issues. Both specify the missing orchestration, evidence, security, progress, and resumability work required.

**Biggest unknown:** The exact existing backlog is not visible this round, so I avoided named backlog items and focused on end-to-end capabilities that require the pendant, always-awake relay, unattended Mac, and authenticated browser together.

