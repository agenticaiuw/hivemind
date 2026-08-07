# Harness derivation — mac-terminal — round 42

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent readiness and diagnostics** — Fresh /ops/snapshot reports fullControlMode=true and relay reachable, but computerUse loop disabled; Accessibility and Screen Recording are not trusted, browser extension offline with 3 pending commands. New granted diagnostic tool schemas exist but both implementations return 'no implementation yet'.
  - evidence: GET /ops/snapshot live response 200; mac_read_diagnostics and mac_readonly_diagnostics_impl calls returned no implementation yet.

## Capabilities it proposed

### "If a task gets interrupted, continue it from where it stopped and tell me what was completed, what remains, and whether anything needs my decision."
- **useful because:** Today a dropped Mac connection, sleeping laptop, or offline browser leaves the owner unsure whether work happened. Durable checkpoints let the pendant, relay, Mac, and browser act as one assistant instead of restarting or silently losing progress.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for checkpoint reconciliation and summaries; realtime only for the pendant's short status answer
- **latency:** Immediate acknowledgement on the pendant (<1 s); reconcile within 10-30 s after a node reconnects; no need to keep a realtime model running.
- **cost:** Usually <$0.01 per interrupted task; dominant cost is one background reconciliation/completion-summary call, with deterministic receipt merging for normal cases.
- **security:** Checkpoint records may contain private page snippets, shell output, and draft text. Keep raw evidence on the originating Mac/browser, send signed hashes and least-privilege summaries through relay, encrypt durable state, and require explicit owner confirmation only when resumption would create an external irreversible side effect.
- **missing:** A shared durable task DAG with per-step checkpoint, idempotency key, and completion evidence; Mac shell envelope and resumable failed-step endpoint; Browser extension reconnect/command replay with tab-session affinity; Relay lease/heartbeat and crash recovery for jobs; Pendant status intent such as 'what happened?' and 'continue'; Dashboard timeline showing completed, skipped, failed, and awaiting-decision steps

### "Let me start a task by voice on the pendant, pick it up on my Mac or in the browser, and hand it back to the pendant with the exact current state, evidence, and next choice preserved."
- **useful because:** The owner should not have to repeat context when moving from walking to desk work or from a spoken request to a logged-in webpage. This creates a real shared workspace across devices: the pendant captures intent, the relay preserves the task, the Mac and browser do the work, and any surface can present the same truthful state.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic state synchronization and evidence merging first; use a background model to summarize the handoff and a planner-tier model only when the next action is ambiguous. Realtime is limited to the initial voice interaction.
- **latency:** Voice acknowledgement under 1 second; switching surfaces should show the current task within 2 seconds after reconnect; reconciliation after a disconnected node returns may take 10-30 seconds.
- **cost:** Typically under $0.01 per handoff. Most transfers are deterministic; cost is dominated by an occasional short background summary of new evidence.
- **security:** The shared task may contain authenticated-page data, shell output, drafts, or personal context. Bind each task to the owner's paired devices, encrypt relay state, keep raw evidence local to the originating surface, expose sensitivity labels, and require confirmation before revealing private browser content on a less-trusted surface or executing an irreversible next step.
- **missing:** A first-class task identity and versioned state protocol shared by pendant, relay, Mac, and browser; Conflict-free event log with causality, leases, and explicit stale-state detection; Evidence references that remain valid across surfaces without copying sensitive raw content; Cross-surface handoff UI and pendant commands for list, switch, pause, and resume; Authenticated device-pairing and per-surface disclosure policy; Recovery semantics when two surfaces attempt the next step concurrently


## Changes it proposed to its own stack

### `mac-harness` — Add a non-blocking shell execution envelope around every run_shell call (without changing FULL_CONTROL_MODE): record exact command, resolved cwd, start/end timestamps, timeout, exit code/signal, stdout/stderr byte counts plus redacted preview and content hashes, environment fingerprint (keys only), action-risk label, and an automatic retry classification. Persist it in the existing job receipt/journal and expose a 'resume failed job' endpoint that retries only the failed step with the same idempotency key and prior evidence attached.
- **owner gets:** When a command fails or the Mac link drops, the pendant can say exactly what happened instead of guessing, and can resume a long task rather than making the owner repeat it. The owner keeps unrestricted capability; this only makes shell behavior explainable and recoverable.
- effort: Medium: executor wrapper, receipt schema, journal projection, retry endpoint, and relay-safe summary formatter.  ·  risk: Command text and output can contain secrets; store full output only locally with short retention, send hashes and redacted previews to relay, and support deletion. Retrying arbitrary commands can duplicate side effects, so default resume is only for a step marked failed before confirmed completion; preserve the current no-gate policy.
- cost: Negligible storage and one cheap background classification call only when a failure occurs; no additional realtime calls.  ·  latency: ~5-20 ms local bookkeeping; retries add only the command's own runtime.
- security: Improves auditability without narrowing access. Requires secret scrubbing and strict local receipt permissions.
- depends on: existing actionReceipts/jobTracker/journal integration; relay job status and idempotency plumbing; a durable step/checkpoint representation for multi-action jobs


## What it asked for

### `t16-xmaf` (tool) — mac_readonly_diagnostics_impl
- why: The orchestrator granted this read-only diagnostic schema, but invocation currently returns 'no implementation yet'. I need bounded host facts to verify whether the Mac-agent readiness and permission state changed, without arbitrary shell.

```json
{
  "type": "object",
  "properties": {
    "checks": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "os_version",
          "hardware_model",
          "current_user",
          "uptime",
          "battery",
          "network_interfaces",
          "wifi_status",
          "bluetooth_devices",
          "audio_devices",
          "local_agent_health",
          "running_process_summary",
          "disk_space"
        ]
      },
      "maxItems": 8
    }
  },
  "required": [
    "checks"
  ],
  "additionalProperties": false
}
```

