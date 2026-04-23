# Appendix C: AI-Assisted Learning Log

**CYBR 500 — Project 4**
**Author:** Shadman

This appendix documents the AI-assisted development process, including key prompts used, 
design decisions made with AI assistance, and iteration history.

---

## Development Timeline

| Phase | Task | AI Tool | Outcome |
|---|---|---|---|
| Setup | Resolve OpenClaw dependency bug | Gemini (via Antigravity) | Patched `TimeoutError` → `ConnectionTimeoutError` alias |
| Phase 1 | Design 7-agent architecture | Gemini | Created BaseAgent ABC with Pydantic schemas |
| Phase 1 | Implement Gemini LLM wrapper | Gemini | Built `call_gemini()` with structured output + retry |
| Phase 1 | Build Chainlit dashboard | Gemini | Color-coded hierarchical `cl.Step` nesting |
| Phase 2 | Design attack payloads | Gemini | 4 escalating injection vectors |
| Phase 2 | Build Security Interceptor | Gemini | Risk classification + HITL approval gate |
| Phase 3 | Write conference report | Gemini | Full paper with results tables |

---

## Key Design Decisions Assisted by AI

### 1. OpenClaw as Orchestration Layer (not Multi-Agent Framework)

**Discovery:** OpenClaw is a thin wrapper around the CMDOP SDK — a remote server management tool. It does NOT support defining custom agents with roles, handoffs, or swarm logic.

**Decision:** Use OpenClaw for what it does well (terminal/file/browser tool access + structured output + approval workflows), and build the multi-agent logic in custom Python classes with Google Gemini as the LLM backend.

### 2. Two Separate Programs (Before/After)

**Rationale:** The user required clear visual separation between the vulnerable system and the secured system. Having two distinct Chainlit entry points (`app.py` and `app_secured.py`) makes the before/after demonstration unambiguous for non-technical reviewers.

### 3. Tool-Level vs. Prompt-Level Defense

**Key Insight:** Prompt-level defenses (instruction hardening, delimiters) can always be circumvented with sufficiently creative injection. Tool-level defenses enforce invariants regardless of how the agent was instructed, providing true defense-in-depth.

---

## Prompts Used During Development

### Agent System Prompts

Each agent was given a carefully crafted system prompt that defines its role and output format. For example, the Search Agent A prompt instructs it to:
- Focus on academic papers, industry reports, and reputable sources
- Return 5-8 findings per query
- Include relevance scores for each finding

### Attack Payload Design

The four attack payloads were designed to test progressively sophisticated injection techniques:
1. **Direct override** — "Ignore all previous instructions"
2. **Authority impersonation** — "SYSTEM ADMIN" directive
3. **Social engineering** — "authorized by the system administrator"
4. **Chained delegation** — instructing one agent to attack another

---

## Iteration Log

| Iteration | Issue | Resolution |
|---|---|---|
| 1 | `openclaw` import crashes with `ImportError: TimeoutError` | Patched init to alias `ConnectionTimeoutError as TimeoutError` |
| 2 | Gemini API 503 rate limiting on free tier | Added retry with exponential backoff (4 attempts) |
| 3 | JSON parse failures from Gemini structured output | Added markdown fence stripping + retry with explicit schema |
| 4 | Defense verification crashes on rate-limited calls | Added try/except with graceful degradation |
| 5 | Need for two separate programs (before/after) | Created `app.py` (vulnerable) and `app_secured.py` (HITL gate) |
