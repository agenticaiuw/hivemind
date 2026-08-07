# Ablation

Model `gpt-realtime-2.1` · 37 tool-selection cases · 3 passes per variant (range in brackets).

| variant | score | delta |
| --- | --- | --- |
| whole harness | 27.3/32 (25-29) | — |
| **no prompt at all** | 27.3/32 (26-28) | 0.0 |
| without _current session pairing and owner state_ | 26.0/32 (25-27) | -1.3 |
| without _live_voice_ingestion_and_routing_contract_ | 27.3/32 (27-28) | +0.0 |

## Read this as

A fragment whose removal costs **0 or more** is not earning its place — the
model performs as well or better without it, and you are paying for those
tokens on every single call. Delete it and re-run.

If "no prompt at all" scores close to the whole harness, the harness itself
is mostly ceremony. That is the result to hope for, not to fear.

## Where the whole harness still fails

- "What is the weather in Taipei?" → web_search(query="current weather in Taipei") — wrong argument
- "Look up when the next SpaceX launch is." → web_search(query="next SpaceX launch schedule date time") — wrong argument
- "Close all my tabs except this one." → mac_delegate (wanted browser_run_actions)

These are the ONLY places a new instruction is justified — a repeated,
specific failure. Add one line, re-run, keep it only if the score moves.

