# Harness derivation — relay-realtime — round 41

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep this task with me as I move between places: capture my spoken goal now, continue it on the first available Mac and authenticated browser, and give me a spoken, resumable handoff if either device disappears.”"
- **useful because:** Today a task handed off from the worn pendant can become opaque when the Mac is asleep, accessibility is unavailable, or the browser extension is offline. The owner needs one durable conversational task identity: the pendant preserves the exact goal and constraints, the relay tracks which substrate is currently reachable, the Mac acts when available, and the browser contributes authenticated context when it returns. If execution pauses, the owner hears a concise reason and can resume without repeating the request; if it completes, they get a receipt tied to the same spoken task.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay for capture, interruption notices, and short spoken updates; gpt-5.6-luna mac-planner for decomposition and recovery; gpt-4.1-mini mac-vision only for visual UI steps; a cheaper background model for compressing checkpoints and producing the final spoken receipt.
- **latency:** Acknowledge capture on the pendant in under 500 ms. Route immediately when a substrate is online; reconnect/resume within 5 seconds of a device heartbeat. Checkpointing and receipt summarization may take seconds in the background.
- **cost:** About $0.01–$0.05 per task in planner/background inference, with realtime tokens only for the initial acknowledgement and exceptions. Browser and Mac execution dominate wall-clock time, not model spend.
- **security:** The relay must store encrypted task checkpoints, not browser cookies or raw page secrets. Authenticated page content should stay in the browser harness and only typed findings should cross the relay. Device return and task identity need authenticated pairing to prevent another nearby Mac or stale browser tab from accepting work. Destructive external actions remain attributable in receipts and should be surfaced clearly, while honoring the owner's existing no-confirmation preference for reversible work.
- **missing:** A durable cross-substrate task record containing goal, constraints, checkpoint, provenance, and resumable state; Connectivity-aware dispatch and lease/heartbeat protocol across relay, Mac, and browser; Pendant-local short-term capture/replay when LTE drops, plus a compact LED/button resume/error vocabulary; Browser-side authenticated handoff that can return typed page findings to the same task without exposing session secrets; Mac planner recovery semantics for partial completion, duplicate prevention, and a human-readable completion receipt; Dashboard timeline showing task ownership, pause reason, last checkpoint, and final evidence


## What it asked for

_Nothing._
