# Harness derivation — mac-vision — round 2

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

- **agent and machine environment** — Agent is AI Pendant Mac Local Agent v0.5.0 with full control mode and LLM planner enabled. ComputerUse loop is currently disabled with maxSteps=25. Agent has accessibility and screen recording permissions granted. Machine hostname is MacBook-Air-6.local. Machine platform is darwin (Mac). 123 apps installed, including AI Pendant and various common apps like Safari and Microsoft Office. Browser extension (Safari) version 1.2.0 is online with no open tabs or pending commands. Relay cloud service is configured and reachable.
  - evidence: Response from GET /ops/status with detailed agent, machine, permissions, browser, and relay info.

## What it asked for

_Nothing._
