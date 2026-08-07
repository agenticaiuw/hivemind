# Harness derivation — faculty-judgement — round 3

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac readiness** — Mac local agent is reachable and relay is configured/reachable, but actual readiness is false: Accessibility and Screen Recording are not granted, and browser extension is offline. Therefore GUI/browser workflows cannot safely be promised yet.
  - evidence: GET /ops/status returned agent ready:false, accessibility.trusted:false, screenRecording.granted:false, browserExtension.online:false; GET /browser/status returned online:false.
- **audio architecture** — The current prototype already renders downlink speech as 24 kHz mono PCM, but the pendant decodes Opus at 24 kHz then outputs via a 31,250 Hz I2S wire clock; ESP32 resamples 31,250 to 44,100 for SBC Bluetooth. LTE-M contention has dropped 7.8 seconds of uplink speech in a measured call.
  - evidence: get_hardware_spec(audio), get_hardware_spec(bridge), and get_hardware_spec(network) returned these measured implementation details.
- **offline resilience** — Pendant stores failed uploads on microSD and later surfaces held alerts/bookmarks; pipeline telemetry shows offline-store alert delivery events. Storage is intended as failure buffer, not routine audio retention.
  - evidence: get_hardware_spec(storage) and GET /pipeline returned microSD policy plus alert_delivered/bookmark events with origin pendant-offline-store.
- **owner priorities** — Owner's remembered current goal is to derive next changes from the harness ledger and ship the 24 kHz superwideband audio path end to end; they also have an idea for a pendant that files its own UART-log bug reports.
  - evidence: discover(owner) returned remembered Now and Relevant entries.

## What it asked for

### `c1-stec` (context) — current harness-ledger priorities and audio acceptance criteria
- why: The owner's remembered Now says to derive the next changes from the harness ledger and ship the 24 kHz superwideband path end to end, but reconnaissance exposes only summaries and prototype hardware limits. I need the authoritative accepted/rejected ledger entries and target definition to judge the next build rather than duplicate old proposals.
- would change: I will prioritize only ledger items still actionable, and evaluate audio changes against an explicit acceptance target (sample rates, packet loss/jitter tolerance, latency, and whether the 31.25 kHz I2S/44.1 kHz SBC bridge may change).

### `t2-zs14` (tool) — pendant_diagnostics_and_bug_draft
- why: The owner explicitly has the idea of a pendant that files its own bug reports from the UART log. Existing production tools cover Mac/browser/research/status but do not expose a safe, structured UART-log parser or issue-draft workflow. This is useful even before automatic filing: detect anomalies, correlate link/audio metrics, and produce a reviewable draft without sending externally.

```json
{
  "type": "object",
  "properties": {
    "since": {
      "type": "string",
      "description": "ISO timestamp, duration (for example 'last 30m'), or log cursor from which to inspect UART/diagnostic records"
    },
    "include_audio_metrics": {
      "type": "boolean",
      "description": "Include packet loss, queue depth, underruns, sample-rate transitions, and latency evidence"
    },
    "draft_target": {
      "type": "string",
      "enum": [
        "local_note",
        "github_issue_draft",
        "email_draft",
        "none"
      ],
      "description": "Where to prepare a reviewable draft; never send or submit"
    },
    "severity_threshold": {
      "type": "string",
      "enum": [
        "info",
        "warning",
        "error",
        "critical"
      ],
      "description": "Minimum severity to include"
    },
    "spoken_reply": {
      "type": "string",
      "description": "Short user-facing status sentence"
    }
  },
  "required": [
    "since",
    "draft_target"
  ]
}
```

## Its own summary

Reconnaissance confirms a reachable Mac agent and Cloudflare relay, but the system is not actually ready for GUI/browser work: /ops/status reports Accessibility and Screen Recording false and browser extension offline. The owner’s key priority is 24 kHz superwideband end-to-end audio. Current evidence shows downlink speech rendered at 24 kHz, pendant Opus decode at 24 kHz, but a 31.25 kHz I2S wire clock and ESP32 resampling to 44.1 kHz SBC; LTE-M contention has caused 7.8 s uplink loss. I recorded these findings, requested authoritative harness-ledger/audio acceptance context, and requested a safe structured UART diagnostics/bug-draft capability. Still needed from the orchestrator: actually verify/reapply Accessibility + Screen Recording and reconnect the browser bridge (the probe contradicts the claimed grants), plus provide the ledger priorities and audio acceptance criteria.

**Biggest unknown:** Which harness-ledger changes are still accepted/actionable, and what exact definition of “24 kHz superwideband end to end” is required—especially whether the 31.25 kHz I2S clock and 44.1 kHz SBC bridge are permitted or must be replaced.

