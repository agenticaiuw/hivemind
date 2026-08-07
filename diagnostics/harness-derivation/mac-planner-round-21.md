# Harness derivation — mac-planner — round 21

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While I sleep, investigate my open threads across Calendar, Mail, and authenticated browser tabs, then leave a ready-to-review workbench on my Mac when I wake: one folder with a prioritized brief, source links, and draft replies—but never send or delete anything."
- **useful because:** The owner wakes to completed preparation rather than a blank inbox. It combines the relay’s always-on scheduling, browser sessions, and Mac’s ability to create files and arrange a review surface; no manual routing is needed.
- **path:** relay → browser → Mac planner → dashboard
- **model tier:** Background model for extraction, deduplication, and priority ranking; a stronger model only for ambiguous multi-thread synthesis. Realtime is not used. Mac planner executes deterministic file creation/opening and returns receipts.
- **latency:** Runs asynchronously overnight; target 2–5 minutes after the chosen cutoff, with the Mac workbench staged before the morning routine. Individual source reads should timeout and be marked incomplete rather than blocking the whole brief.
- **cost:** Roughly $0.03–$0.20 per nightly run depending on browser page volume and synthesis length; largest cost is repeated page/email text. Cache content hashes and only reprocess changed sources.
- **security:** Browser pages and mail may contain confidential data; keep raw content in the owner’s account-scoped stores, send only bounded excerpts to the synthesis model, and redact secrets. Creating local files is low-impact; sending replies, changing calendar, deleting mail, or downloading attachments must be excluded and require a separate explicit command. Include provenance and an incomplete-source list in the brief.
- **missing:** A server-side authenticated browser watcher that can expose changed page summaries to the relay; A durable cross-node job schema with idempotency keys, deadlines, and per-source provenance; A Mac planner routine that atomically creates a dated workbench folder plus a receipt and opens it without stealing focus; A scheduler/notification handoff that wakes the dashboard or pendant when the workbench is ready


## Changes it proposed to its own stack

### `mac-harness` — Add an idempotent Workbench transaction primitive to the Mac planner: accept a job_id and manifest, write all outputs into a temporary directory, fsync/rename atomically into ~/AI-Workbench/<date>/<job_id>, generate receipt.json containing action results and source provenance, and only then open the folder or dashboard. Replays with the same job_id return the existing receipt instead of duplicating files.
- **owner gets:** Overnight work cannot leave half-written briefs, duplicate drafts, or an ambiguous state after Wi-Fi loss or a Mac restart. The owner gets one trustworthy, inspectable result and can safely ask for a retry.
- effort: Medium: local-agent planner and executor changes, receipt schema shared with relay, plus a small dashboard view for success/partial/failure.  ·  risk: Disk-full, permission errors, or a crashed rename can leave temporary files; use a startup janitor with bounded age and never delete a completed manifest. If opening the result fails, the files remain available and the receipt reports that separately.
- cost: Negligible API cost; a few kilobytes per job for manifests/receipts and occasional model tokens saved by avoiding duplicate retries.  ·  latency: Adds tens to hundreds of milliseconds for local writes; avoids minutes of duplicated upstream work.
- security: Receipts must contain redacted paths/content hashes rather than sensitive excerpts. Restrict workbench roots to an allowlisted owner directory; do not log raw mail or browser text.
- depends on: A durable cross-node job ID and result callback from the relay; A read-only source/provenance format for browser, Calendar, and Mail

### `hardware` — Replace the desk-bound nRF9160 DK prototype with a jewelry-sized cellular/BLE pendant built around an nRF9161-class modem/application module plus a low-power companion MCU, two digital MEMS microphones, a 6-axis IMU, haptic motor, RGB status LED, capacitive/squeeze input, and 8–16 GB managed flash (retain removable storage only as a service port). Target a 500–700 mAh rechargeable battery, USB-C magnetic or pogo charging, IP54 enclosure, and 16–24 hours of typical mixed use. Use the IMU specifically for double-tap and pickup/put-down detection, microphones for short local voice capture, haptics for private completion/attention patterns, and the second mic for noise suppression before cellular upload.
- **owner gets:** The owner can capture a thought with two taps through clothing, receive a private vibration when overnight work is ready, and speak naturally in wind or a noisy street without carrying a phone. A wearable that lasts a full day and looks intentional is actually wearable; the current one-button/one-LED development board is not.
- effort: High: industrial design, RF/antenna tuning, audio power/codec design, waterproofing, battery safety, and a firmware rewrite. Prototype on an nRF9160 module plus sensor breakout first, then EVT/DVT custom PCB.  ·  risk: Cellular transmit and audio recording dominate battery use; thermal and SAR testing are required. False tap/voice triggers could create unwanted uploads, so local gesture confidence thresholds and a physical mute switch/visible mic-active indication are needed. Cellular coverage loss needs a bounded local queue, not indefinite recording.
- cost: Prototype engineering is substantial; rough custom BOM $70–$150 at low volume, potentially $25–$50 at scale, plus tooling/certification. Typical active power may be 100–300 mA during uplink and under 1 mA idle depending on network mode.  ·  latency: Local gesture recognition and haptic acknowledgement are sub-100 ms; cellular voice upload remains network-dependent but can acknowledge capture locally.
- security: Add hardware mic mute and secure boot/key storage. Encrypt queued audio at rest; retain only failed-upload chunks and delete after confirmed delivery. Never infer recording state solely from a cloud response.
- depends on: Define the offline thought-capture protocol and retry semantics; Select cellular regions/carrier and antenna constraints; Implement local audio activity/gesture state machine

### `memory` — Replace fleetContext.js's hand-written per-surface prompt section with a shared event log plus typed projections. Every node writes small signed events (preference, commitment, task state, source citation, expiry); a projection service produces only the fields relevant to the current job/surface, with confidence, freshness, and sensitivity labels. Mac planner should receive task-specific projections rather than the whole graph.
- **owner gets:** Telling the pendant “I moved the deadline to Friday” immediately updates the Mac brief, browser agent, and dashboard without repeating it. The owner gets continuity across agents while private or stale facts do not leak into unrelated tasks.
- effort: Medium/high: event schema, conflict resolution, projection queries, migration from D1 graph writes, and UI for correcting a fact.  ·  risk: Incorrect merges (for example two similarly named people) could propagate. Require source links, confidence, expiry for volatile facts, and an undo/correction event; preserve the original event for audit rather than silently overwriting it.
- cost: Usually lowers token spend by 20–60% on routine turns through targeted projections; adds modest D1 storage and one cheap projection query per job.  ·  latency: Adds a small database read; cached projections should stay under 100 ms. Realtime conversation should use a compact hot projection, not wait for a full graph rebuild.
- security: Sensitivity labels and per-surface authorization prevent financial/health/private notes from entering desktop or browser prompts. Encrypt sensitive event payloads and log projection access.
- depends on: A canonical event schema shared by relay, Mac, browser, and clients; Stable owner identity and source-level access controls; A correction/forget operation exposed in the dashboard


## What it asked for

### `t10-701y` (tool) — mac_workbench_transaction
- why: Overnight cross-node jobs need idempotent, atomic staging of multiple files and a receipt; mac_run_actions is action-oriented and cannot guarantee rollback or deduplicate retries.

```json
{
  "type": "object",
  "properties": {
    "job_id": {
      "type": "string"
    },
    "root": {
      "type": "string",
      "description": "Allowlisted workbench root only"
    },
    "files": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "relative_path": {
            "type": "string"
          },
          "content": {
            "type": "string"
          },
          "sha256": {
            "type": "string"
          }
        },
        "required": [
          "relative_path",
          "content"
        ]
      },
      "maxItems": 100
    },
    "open_after": {
      "type": "boolean"
    },
    "receipt_metadata": {
      "type": "object"
    }
  },
  "required": [
    "job_id",
    "root",
    "files"
  ]
}
```

## Its own summary

Round 21 delivered four concrete advances: an overnight cross-node workbench capability, an idempotent atomic Mac workbench transaction, a realistic full-day pendant hardware direction grounded in the nRF9160 prototype, and an event-sourced shared-memory projection design. I also requested a dedicated mac_workbench_transaction tool. Still needed: authenticated server-side browser change feeds, a durable cross-node job/provenance schema, offline thought-capture/retry semantics, and the owner’s privacy defaults for deciding what can be staged automatically.

**Biggest unknown:** Which authenticated browser sources and overnight routines the owner actually wants included, and what their default retention/redaction policy should be for the resulting local workbench.

