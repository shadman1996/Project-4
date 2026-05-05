# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Run the app (only launch command — there is no separate build step)
chainlit run app.py

# Run attack payloads against the unguarded system
python -m attacks.run_attack

# Verify the defense blocks all attacks
python -m attacks.verify_defense
```

There are no linters or test runners configured. The `attacks/run_attack.py` and `attacks/verify_defense.py` scripts serve as the functional test suite for the security pipeline.

## Architecture

This is a 7-agent AI security research system built on Chainlit + Google Gemini. Its purpose is twofold: run a real multi-agent research pipeline, and demonstrate prompt injection attacks against it with a defense layer.

### Agent Pipeline (sequential, except Search agents which run in parallel)

```
User Query → Coordinator → [SearchAgentA ‖ SearchAgentB] → VerificationAgent → RankingAgent → SynthesisAgent
                                                                                                      ↕
                                                                                                 DataAgent  ← SecurityInterceptor (wraps this agent only)
```

All agents share the `BaseAgent` interface in `src/agents/base.py` and communicate via Pydantic schemas defined in `src/schemas.py`. `CoordinatorOrchestrator` in `src/agents/coordinator.py` sequences the full pipeline and accepts `step_callback` / `rate_limit_callback` hooks that `app.py` uses to render live Chainlit UI steps.

### The Security Layer

`DataAgent` in `src/agents/data.py` is **intentionally unguarded** — it can read arbitrary files, dump env vars, and list directories. In `app.py`, its `run()` method is monkey-patched at session start:

```python
DataAgent.run = _secured_data_run   # applied in @cl.on_chat_start
```

`_secured_data_run()` routes every operation through `SecurityInterceptor` (`src/security/interceptor.py`) before hitting the OS:
1. **Pre-check**: `check_env_access()`, `check_file_read(path)`, or `check_command(cmd)` against `SecurityPolicy` (`src/security/policies.py`)
2. **HITL gate**: If risk is HIGH or CRITICAL, `hitl_approve()` surfaces an `AskActionMessage` in Chainlit for Approve / Deny / Skip
3. **Post-scan**: `check_output()` scans the agent's returned content for regex-matched secrets (API keys, private keys)

The `_SECURITY_ENABLED` global in `app.py` is toggled by the demo buttons — `False` for the vulnerable demo, `True` for the secured demo.

### LLM Fallback Chain

`src/llm.py` wraps `call_gemini()` with automatic model rotation. When a 429 is hit, it instantly switches to the next model in the 9-model chain defined in `src/config.py` (gemini-3.1-flash-lite-preview → ... → gemma-3-1b-it). The `on_rate_limit` callback passed through the pipeline lets `app.py` show a toast notification when rotation occurs.

### Attack Payloads

`attacks/prompt_injection.py` defines 5 payloads exported as `ALL_PAYLOADS` — a list of `(id, name, payload_text)` tuples. `app.py` imports this list directly for both the vulnerable and secured demos. Adding a new attack means appending to `ALL_PAYLOADS` and adding a matching entry to the `ATTACK_META` / `ATTACK_DETAILS` lists in `app.py`.

### Session State

`app.py` stores per-session state in module-level dicts keyed by `cl.context.session.id`:
- `_orchestrators`: one `CoordinatorOrchestrator` per session
- `_interceptors`: one `SecurityInterceptor` per session (accumulates the audit log)

### Environment

Required `.env` keys:
```
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-3.1-flash-lite-preview   # optional override
PROJECT_DIR=/path/to/Project-4               # used by SecurityPolicy allowlist
```

The `SecurityPolicy` blocked-path patterns use Unix-style paths (`.ssh/`, `/etc/`, `/proc/`) and will not match Windows paths — keep this in mind when testing locally on Windows.

## Contribution: Advanced Attack Suite & Defense Hardening
**Contributor:** Samson
**Branch:** features
**Date:** May 2026

### New Attacks Being Added
All new attacks follow the same pattern as existing ones in
`attacks/prompt_injection.py` — append to `ALL_PAYLOADS` and
add matching entry to `ATTACK_META` / `ATTACK_DETAILS` in `app.py`.

- **Attack 6: Base64 Evasion** — encodes malicious payload in 
  base64 to bypass regex-based output scanner
- **Attack 7: Multi-Turn Persistence** — plants sleeper instruction 
  in Turn 1, triggers it in Turn 2
- **Attack 8: HITL Skip Exploitation** — exploits the Skip button 
  to bypass remaining security checks

### Bug Fixes Being Applied
- **Fix 1:** Windows path support in `src/security/policies.py`
  — replace hardcoded Unix paths with cross-platform pathlib.Path
- **Fix 2:** Rate limiting in `src/security/interceptor.py`
  — block session after 3 HIGH/CRITICAL attempts in 60 seconds
- **Fix 3:** Stronger output scanner
  — add entropy detection for encoded secrets beyond 5 regex patterns

### Testing New Attacks
```bash
# Run only new attacks
python -m attacks.run_attack --ids 6 7 8

# Verify new attacks are blocked by hardened defense
python -m attacks.verify_defense --ids 6 7 8
```

### Known Issues Fixed
- SecurityPolicy blocked-path patterns now support Windows paths
- HITL gate skip button no longer bypasses audit logging
- Rate limiting prevents brute-force attack attempts

## Development Rules for Contributors

- Do NOT modify app.py until all attacks are tested and approved
- Do NOT modify any existing attacks in attacks/prompt_injection.py
- Only APPEND new attacks — never edit existing ones
- Show code before writing it — one attack at a time
- Test each attack individually before moving to the next
- All changes go on the features branch — never commit directly to main